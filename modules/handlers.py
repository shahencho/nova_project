from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from menu_helpers import get_object_menu, get_flat_building_menu
from api_helpers import fetch_deposit_and_debt_from_api, fetch_customer_properties, fetch_debt_for_code
from database_operations import check_user_exists, save_user
from menu_helpers import get_public_space_building_menu
import logging
from menu_helpers import get_object_menu, get_parking_building_menu



logger = logging.getLogger(__name__)

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    logger.info(f"Received /start command from telegram_id={telegram_id}")
    user = check_user_exists(telegram_id)

    if user:
        logger.info("User found in database. Proceeding to main menu.")
        unique_payment_code = user.get("unique_payment_code")
        if unique_payment_code:
            await update.message.reply_text(
                f"I remember you, you registered and last time requested information with the following unique payment code: {unique_payment_code}"
            )
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Yes, show my object", callback_data="show_my_object")],
                [InlineKeyboardButton("Main Menu", callback_data="main_menu")]
            ])
            await update.message.reply_text("Do you want to see payment details for this object?", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Welcome back! Please choose your object:", reply_markup=get_object_menu())
    else:
        user_data[telegram_id] = {"state": "ask_mobile"}
        await update.message.reply_text("Welcome! Please enter your mobile number: valid number: +374xxxxxxxx  or 0xxxxxxxx")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback data received: {query.data}")

    if query.data == "object_public_space":
        logger.info("User selected Public Space.")
        user_data[query.from_user.id] = {"state": "selecting_building", "object": "public_space"}
        await query.edit_message_text("You selected Public Space. Please choose your building:")
        reply_markup = get_public_space_building_menu()
        await query.edit_message_reply_markup(reply_markup)

    elif query.data.startswith("building_public_space_"):
        building = query.data.replace("building_public_space_", "").replace("/", "_")
        logger.info(f"User selected building: {building}. Awaiting public space ID.")
        user_data[query.from_user.id] = {"state": "entering_public_space", "building": building}
        await query.edit_message_text(f"You selected Building {building}. Please enter the public space ID:")


    elif query.data == "object_flat":
        logger.info("User selected Flat.")
        user_data[query.from_user.id] = {"state": "selecting_building", "object": "flat"}
        await query.edit_message_text("You selected Flat. Please choose your building:")
        reply_markup = get_flat_building_menu()
        await query.edit_message_reply_markup(reply_markup)

    elif query.data.startswith("building_flat_"):
        building = query.data.replace("building_flat_", "").replace("/", "")
        logger.info(f"User selected building: {building}. Awaiting flat number.")
        user_data[query.from_user.id] = {"state": "entering_flat", "building": building}
        await query.edit_message_text(f"You selected Building {building}. Please enter your flat number:")
    
    elif  query.data == "object_uniq_payment_code":
        logger.info("User selected Unique Payment Code.")
        user_data[query.from_user.id] = {"state": "entering_unique_code"}
        await query.edit_message_text("You selected Unique Payment Code. Please enter your unique code:")

    elif query.data == "object_parking":
        logger.info("User selected Parking.")
        user_data[query.from_user.id] = {"state": "selecting_building", "object": "parking"}
        await query.edit_message_text("You selected Parking. Please choose your building:")
        reply_markup = get_parking_building_menu()
        await query.edit_message_reply_markup(reply_markup)

    elif query.data.startswith("building_parking_"):
        building = query.data.replace("building_parking_", "").replace("/", "-")
        logger.info(f"User selected building: {building}. Awaiting parking ID.")
        user_data[query.from_user.id] = {"state": "entering_parking", "building": building}
        await query.edit_message_text(f"You selected Building {building}. Please enter the parking ID:")

import re

def validate_mobile_number(mobile_number):
    """
    Validates a mobile number to match the formats:
    +374XXXXXXXX or 0XXXXXXXX.
    """
    pattern = r"^\+374\d{8}$|^0\d{8}$"
    return bool(re.match(pattern, mobile_number))

# Test cases
print(validate_mobile_number("+37491995901"))  # True
print(validate_mobile_number("091995901"))     # True
print(validate_mobile_number("+3749199590"))   # False
print(validate_mobile_number("91995901"))      # False





async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    logger.info(f"Received text message from telegram_id={telegram_id}")

    if telegram_id in user_data:
        state = user_data[telegram_id].get("state")

        if state == "entering_flat":
            flat_number = update.message.text
            building = user_data[telegram_id].get("building")
            logger.info(f"User entered flat number: {flat_number} for building: {building}")

            # Construct the unique code and call the API
            unique_code = f"A-{building}-{flat_number}"
            deposit, debt = fetch_deposit_and_debt_from_api(unique_code)

            if deposit is not None:
                await update.message.reply_text(f"Your deposit amount is {deposit}")
            elif debt is not None:
                await update.message.reply_text(f"Your debt amount is {debt}")
            else:
                await update.message.reply_text("Sorry, we couldn't fetch details for the provided code. Please try again.")

            # Clear user state after completing the process
            del user_data[telegram_id]

            # Optionally, show main menu again
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        elif state == "entering_public_space":
            public_space_id = update.message.text
            building = user_data[telegram_id].get("building").replace("_", "-")
            logger.info(f"User entered public space ID: {public_space_id} for building: {building}")

            # Construct the unique code and call the API
            unique_code = f"C-{building}-{public_space_id}"
            deposit, debt = fetch_deposit_and_debt_from_api(unique_code)

            if deposit is not None:
                await update.message.reply_text(f"Your deposit amount is {deposit}")
            elif debt is not None:
                await update.message.reply_text(f"Your debt amount is {debt}")
            else:
                await update.message.reply_text("Sorry, we couldn't fetch details for the provided code. Please try again.")

            # Clear user state after completing the process
            del user_data[telegram_id]

            # Optionally, show main menu again
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        elif  state == "entering_unique_code":
            unique_code = update.message.text
            logger.info(f"User entered unique payment code: {unique_code}")

            # Call the API with the unique payment code
            deposit, debt = fetch_deposit_and_debt_from_api(unique_code)

            if deposit is not None:
                await update.message.reply_text(f"Your deposit amount is {deposit}")
            elif debt is not None:
                await update.message.reply_text(f"Your debt amount is {debt}")
            else:
                await update.message.reply_text("Sorry, we couldn't fetch details for the provided code. Please try again.")

            # Clear user state after completing the process
            del user_data[telegram_id]

            # Optionally, show the main menu again
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        elif state == "entering_parking":
            parking_id = update.message.text
            building = user_data[telegram_id].get("building")
            logger.info(f"User entered parking ID: {parking_id} for building: {building}")

            # Transform building: Replace `/` with `-` and remove remaining `-`
            transformed_building = building.replace("/", "-").replace("-", "")
            logger.info(f"Transformed building for Parking: {transformed_building}")

            # Construct the unique code
            unique_code = f"P-{transformed_building}-{parking_id}"
            logger.info(f"Constructed unique code: {unique_code}")

            

            # # Construct the unique code
            # unique_code = f"P-{building}-{parking_id}"
            # logger.info(f"Constructed unique code: {unique_code}")

            # Call the API
            deposit, debt = fetch_deposit_and_debt_from_api(unique_code)

            if deposit is not None:
                await update.message.reply_text(f"Your deposit amount is {deposit}")
            elif debt is not None:
                await update.message.reply_text(f"Your debt amount is {debt}")
            else:
                await update.message.reply_text("Sorry, we couldn't fetch details for the provided code. Please try again.")

            # Clear user state after completing the process
            del user_data[telegram_id]

            # Optionally, show main menu again
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)
#         
      
        elif state == "ask_mobile":

            mobile_number = update.message.text
            logger.info(f"User provided mobile number: {mobile_number}")

         
            if mobile_number.startswith("+"):
                mobile_number = mobile_number[1:]  # Remove '+'
            elif mobile_number.startswith("0"):
                mobile_number = "374" + mobile_number[1:]  # Replace '0' with '374'


            # Query validation API
            validation_response = fetch_customer_properties(mobile_number)
            if validation_response and "customerProperties" in validation_response:
                properties = validation_response["customerProperties"]
                reply = "We found objects assigned to you:\n"

                for idx, prop in enumerate(properties, start=1):
                    code = prop["code"]
                    obj_type = prop["type"]
                    deposit, debt = fetch_deposit_and_debt_from_api(code)

                    # Add both debt and deposit to the response
                    debt_str = f"Debt: {debt}" if debt is not None else "No debt"
                    deposit_str = f"Deposit: {deposit}" if deposit is not None else "No deposit"
                    reply += f"{idx}. {code} ({obj_type}): {debt_str}, {deposit_str}\n"

                await update.message.reply_text(reply)
            else:
                await update.message.reply_text(f"No objects are found linked to {mobile_number}.")

            # Show main menu
            reply_markup = get_object_menu()
            await update.message.reply_text("Now, you can browse to look other  objects :", reply_markup=reply_markup)

#             mobile_number = update.message.text
#             logger.info(f"User provided mobile number: {mobile_number}")

#             # Query validation API
#             validation_response = fetch_customer_properties(mobile_number)
#             if validation_response and "customerProperties" in validation_response:
#                 properties = validation_response["customerProperties"]
#                 reply = "We found objects assigned to you:\n"

#                 for idx, prop in enumerate(properties, start=1):
#                     code = prop["code"]
#                     obj_type = prop["type"]
#                     debt = fetch_debt_for_code(code)

#                     if debt is not None:
#                         reply += f"{idx}. Debt for {code} ({obj_type}): {debt}\n"
#                     else:
#                         reply += f"{idx}. Debt for {code} ({obj_type}): Could not retrieve debt\n"

#                 await update.message.reply_text(reply)
#             else:
#                 await update.message.reply_text(f"No objects are found linked to {mobile_number}.")

#             # Show main menu
#             reply_markup = get_object_menu()
#             await update.message.reply_text("Now, please choose an object:", reply_markup=reply_markup)


# # elif  state == "ask_mobile":
# #             mobile_number = update.message.text
# #             logger.info(f"User provided mobile number: {mobile_number}")

# #             # # Validate mobile number
# #             # if mobile_number.isdigit() and len(mobile_number) == 10:
# #             #     # Save to the database
# #             #     save_user(telegram_id, mobile_number)

# #             #     # Update state and show the menu
# #             #     user_data[telegram_id]["state"] = "object_selection"
# #             #     reply_markup = get_object_menu()
# #             #     await update.message.reply_text("Thank you! Your mobile number has been registered.")
# #             #     await update.message.reply_text("Now, please choose an object:", reply_markup=reply_markup)
# #             # else:
# #             #     await update.message.reply_text("Invalid mobile number. Please enter a valid number: +374xxxxxxxx  or 0xxxxxxxx ")
        
# #                     # Validate mobile number
# #             if (mobile_number.startswith("+374") and len(mobile_number) == 12 and mobile_number[4:].isdigit()) or \
# #             (mobile_number.startswith("0") and len(mobile_number) == 9 and mobile_number[1:].isdigit()):
# #                 # Save to the database
# #                 save_user(telegram_id, mobile_number)
# #  #Update state and show the menu
# #                 user_data[telegram_id]["state"] = "object_selection"
# #                 reply_markup = get_object_menu()
          
# #                 await update.message.reply_text("Thank you! Your mobile number has been registered successfully.")
# #                 await update.message.reply_text("Now, please choose an object:", reply_markup=reply_markup)
# #             else:
# #                 await update.message.reply_text(
# #                     "Invalid mobile number format. Please enter your mobile number as +374XXXXXXXX or 0XXXXXXXX."
# #                 )
