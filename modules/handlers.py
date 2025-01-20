from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from menu_helpers import get_object_menu, get_flat_building_menu
from api_helpers import fetch_deposit_and_debt_from_api, fetch_customer_properties, fetch_debt_for_code, fetch_property_details
from database_operations import check_user_exists, save_user, update_user_details, validate_and_fetch_mobile_number
from menu_helpers import get_public_space_building_menu
import logging
from menu_helpers import get_object_menu, get_parking_building_menu
from translations import TRANSLATIONS  # Import the translations


logger = logging.getLogger(__name__)

user_data = {}



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    first_name = update.message.from_user.first_name  # Retrieve the user's first name
    logger.info(f"Received /start command from telegram_id={telegram_id} with name={first_name}")
    
    # Fetch and format the welcome message
    welcome_message = TRANSLATIONS["welcome_message"].format(name=first_name)

    user = check_user_exists(telegram_id)
    
    if user:
        logger.info("User found in database. Proceeding to main menu.")
        await update.message.reply_text(welcome_message)
        mobile_number = user.get("mobile_number", "Not available")

    # Combine the messages into one
        x= fetch_customer_properties(mobile_number)

       

        # Extract relevant properties
        customer_properties = x.get("customerProperties", [])
        property_details = "\n".join(
            [f"Code: {prop['code']}, Type: {prop['type']}" for prop in customer_properties]
        )

        # Combine the message
        message = (
            f"{TRANSLATIONS['mobile_saved_in_db_found']} : {mobile_number}\n\n"
            f"{TRANSLATIONS['found_objects']}\n{property_details}"
      
        )

       # message = f"{TRANSLATIONS['mobile_saved_in_db_found']} : Mobile Number: {mobile_number} fetch_customer_properties: {x} "
        await update.message.reply_text(message)

        


        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(TRANSLATIONS["yes_show_objects"], callback_data="show_my_object")],
            [InlineKeyboardButton(TRANSLATIONS["change_mobile"], callback_data="Change_Assosiate_mobile")]

        ])
        await update.message.reply_text(TRANSLATIONS["ask_to_view_details"], reply_markup=reply_markup)

    else:
        user_data[telegram_id] = {"state": "ask_mobile"}
        await update.message.reply_text(welcome_message)
        await update.message.reply_text(TRANSLATIONS["ask_mobile_number"])


from translations import TRANSLATIONS

















async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback data received: {query.data}")

    if query.data == "object_flat":
        logger.info("User selected Flat.")
        user_data[query.from_user.id] = {"state": "selecting_building", "object": "flat"}
        await query.edit_message_text(TRANSLATIONS["choose_flat_building"])
        reply_markup = get_flat_building_menu()
        await query.edit_message_reply_markup(reply_markup)

    elif query.data.startswith("building_flat_"):
        building = query.data.replace("building_flat_", "").replace("/", "-")
        logger.info(f"User selected building: {building}. Awaiting flat number.")
        user_data[query.from_user.id] = {"state": "entering_flat", "building": building}
        await query.edit_message_text(TRANSLATIONS["enter_flat_number"].format(building=building))

    elif query.data == "object_public_space":
        logger.info("User selected Public Space.")
        user_data[query.from_user.id] = {"state": "selecting_building", "object": "public_space"}
        await query.edit_message_text(TRANSLATIONS["choose_public_space_building"])
        reply_markup = get_public_space_building_menu()
        await query.edit_message_reply_markup(reply_markup)

    elif query.data.startswith("building_public_space_"):
        building = query.data.replace("building_public_space_", "").replace("/", "-")
        logger.info(f"User selected building: {building}. Awaiting public space ID.")
        user_data[query.from_user.id] = {"state": "entering_public_space", "building": building}
        await query.edit_message_text(TRANSLATIONS["enter_public_space_id"].format(building=building))

    elif query.data == "object_parking":
        logger.info("User selected Parking.")
        user_data[query.from_user.id] = {"state": "selecting_building", "object": "parking"}
        await query.edit_message_text(TRANSLATIONS["choose_parking_building"])
        reply_markup = get_parking_building_menu()
        await query.edit_message_reply_markup(reply_markup)

    elif query.data.startswith("building_parking_"):
        building = query.data.replace("building_parking_", "").replace("/", "-")
        logger.info(f"User selected building: {building}. Awaiting parking ID.")
        user_data[query.from_user.id] = {"state": "entering_parking", "building": building}
        await query.edit_message_text(TRANSLATIONS["enter_parking_id"].format(building=building))

    elif query.data == "object_uniq_payment_code":
        logger.info("User selected Unique Payment Code.")
        user_data[query.from_user.id] = {"state": "entering_unique_code"}
        await query.edit_message_text("You selected Unique Payment Code. Please enter your unique code:")

    elif query.data == "show_my_object":
        # Retrieve the user's stored mobile number from the database
        user = check_user_exists(query.from_user.id)
        if user and user.get("mobile_number"):
            mobile_number = user["mobile_number"]
            logger.info(f"Handling 'show_my_object' for mobile number: {mobile_number}")
            
            # Call ShowMyObject_based_on_mobile_number with the retrieved mobile number and update object
            await ShowMyObject_based_on_mobile_number(mobile_number, update)
        else:
            logger.warning(f"No mobile number found for user {query.from_user.id}")
            await query.edit_message_text("No mobile number linked to your account. Please restart and provide a mobile number.")

    
    elif query.data.startswith("view_details_"):
        # Extract the unique code from the callback data
        code = query.data.replace("view_details_", "")
        logger.info(f"Handling details for object code: {code}")

        # Fetch detailed property info
        details = fetch_property_details(code)

        if details and isinstance(details, dict):
            logger.info(f"Fetched property details for {code}: {details}")

            # Generate payment history
            transactions = details.get("transactionsPayInfo", [])
            if transactions:
                history = "\n".join([
                    f"{trans['payedDate']}: {trans['payedAmount']}" for trans in transactions
                ])
                # message = f"Payment History for {code}:\n{history}"
                message = TRANSLATIONS["payment_history"].format(code=code, history=history)

            else:
                # message = f"Payment History for {code}: No transactions found."
                message = TRANSLATIONS["no_transactions"].format(code=code)


            # Add Back button
            # back_button = [[InlineKeyboardButton("Back to Objects", callback_data="go_back_to_objects")]]
            back_button = [[InlineKeyboardButton(TRANSLATIONS["back_to_objects"], callback_data="go_back_to_objects")]]

            reply_markup = InlineKeyboardMarkup(back_button)
            await query.edit_message_text(message, reply_markup=reply_markup)
        else:
            logger.error(f"Failed to fetch details for code: {code}")
            await query.edit_message_text("Failed to fetch details. Please try again later.")

    

    elif query.data == "Change_Assosiate_mobile":
        logger.info("User opted to change associated mobile number.")
        user_data[query.from_user.id] = {"state": "changing_mobile"}
        # await query.edit_message_text("Please enter your new phone number in the format +374xxxxxxxx or 0xxxxxxxx.")
        # await update.message.reply_text(TRANSLATIONS["enter_new_mobile"])
        await update.callback_query.edit_message_text(TRANSLATIONS["enter_new_mobile"])



    elif query.data == "go_back_to_objects":
        logger.info("User clicked Back to Objects.")
        user = check_user_exists(query.from_user.id)
        if user and user.get("mobile_number"):
            await ShowMyObject_based_on_mobile_number(user["mobile_number"], update)
        else:
            logger.warning(f"No mobile number found for user {query.from_user.id}")
            await query.edit_message_text("No mobile number linked to your account. Please restart and provide a mobile number.")





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

async def respond_with_payment_info(update, building, object_number, unique_code, deposit, debt):
    """
    Sends detailed payment response to the user based on deposit and debt.

    Args:
        update (Update): The Telegram Update object.
        building (str): The building number.
        object_number (str): The flat/public space/parking ID.
        unique_code (str): The unique code for the object.
        deposit (float): The deposit amount.
        debt (float): The debt amount.
    """
    if debt > 0:
        return (
            f"Building number: {building}, object number: {object_number}, code for this object is: {unique_code}, "
            f"and debt = {debt}. You should hurry up and do the payment ASAP!"
        )
    elif debt == 0 and deposit > 0:
        return (
            f"Building number: {building}, object number: {object_number}, code for this object is: {unique_code}, "
            f"Thanks for not having any debt!"
        )
    elif debt == 0 and deposit == 0:
        return (
            f"Building number: {building}, object number: {object_number}, code for this object is: {unique_code}, "
            f"Thanks for not having any debt!"
        )
    else:
        return (
            f"Sorry, we couldn't fetch details for the provided object:\n"
            f"Building number: {building}, object number: {object_number}, code for this object is: {unique_code}. "
            f"Please try again."
        )

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from api_helpers import fetch_customer_properties, fetch_debt_for_code
import logging

logger = logging.getLogger(__name__)



async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    logger.info(f"Received text message from telegram_id={telegram_id}")

    if telegram_id in user_data:
        state = user_data[telegram_id].get("state")

        if state == "entering_flat":
            flat_number = update.message.text
            building = user_data[telegram_id].get("building")
            logger.info(f"aaaaaaaaaaassssssbuilding before trasnfor : {building}")
            transformed_building = building.replace("-", "")  # Remove `/` for flat
            unique_code = f"A-{transformed_building}-{flat_number}"  # Construct unique code
            logger.info(f"Constructed unique code for Flat: {unique_code}")
            deposit, debt = fetch_deposit_and_debt_from_api(unique_code)
            await respond_with_payment_info(update, transformed_building, flat_number, unique_code, deposit, debt)
            del user_data[telegram_id]
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

           


        elif state == "entering_parking":
            parking_id = update.message.text
            building = user_data[telegram_id].get("building")
            transformed_building = building.replace("-", "")  # Correct logic: Remove `/`
            unique_code = f"P-{transformed_building}-{parking_id}"  # Correct unique code
            logger.info(f"Constructed unique code for Parking: {unique_code}")
            deposit, debt = fetch_deposit_and_debt_from_api(unique_code)
            await respond_with_payment_info(update, transformed_building, parking_id, unique_code, deposit, debt)
            del user_data[telegram_id]
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        elif state == "entering_public_space":
            public_space_id = update.message.text
            building = user_data[telegram_id].get("building")
            transformed_building = building.replace("-", "-")  # Correct logic: Replace `/` with `-`
            unique_code = f"C-{transformed_building}-{public_space_id}"  # Correct unique code
            logger.info(f"Constructed unique code for Public Space: {unique_code}")
            deposit, debt = fetch_deposit_and_debt_from_api(unique_code)
            await respond_with_payment_info(update, transformed_building, public_space_id, unique_code, deposit, debt)
            del user_data[telegram_id]
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        elif state == "entering_unique_code":
            unique_code = update.message.text
            logger.info(f"User entered unique payment code: {unique_code}")
            
            # Fetch deposit and debt using the unique code
            deposit, debt = fetch_deposit_and_debt_from_api(unique_code)
            await respond_with_payment_info(update, "-", "-", unique_code, deposit, debt)  # Building and object_number are placeholders
            del user_data[telegram_id]
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        elif state == "ask_mobile":
            new_mobile_number = update.message.text
            logger.info(f"User provided new mobile number: {new_mobile_number}")

            # Validate and fetch mobile number
            is_valid = await validate_and_fetch_mobile_number(new_mobile_number)
            if not is_valid:
                await update.message.reply_text(TRANSLATIONS["ask_mobile_number"])
                return

            # Save valid mobile number in the database
            save_user(telegram_id, new_mobile_number)
            logger.info(f"Saved mobile number {new_mobile_number} for user telegram_id={telegram_id}")

            # await update.message.reply_text(f"Your mobile number {new_mobile_number} has been saved.")
            await update.message.reply_text(TRANSLATIONS["mobile_number_saved"].format(new_mobile_number=new_mobile_number))

            await ShowMyObject_based_on_mobile_number(new_mobile_number, update)


        elif state== "show_my_object":
            # Update user state (optional, if needed for tracking)
            user_data[query.from_user.id] = {"state": "showing_objects"}

        elif state == "changing_mobile":

            new_mobile_number = update.message.text
            logger.info(f"User provided new mobile number: {new_mobile_number}")

            # Validate and fetch mobile number
            is_valid = await validate_and_fetch_mobile_number(new_mobile_number)
            if not is_valid:
                await update.message.reply_text(TRANSLATIONS["ask_mobile_number"])
                return

            # Update the mobile number in the database
            update_user_details(telegram_id, mobile_number=new_mobile_number)
            logger.info(f"Updated mobile number in the database for telegram_id={telegram_id}")

            # await update.message.reply_text(f"Your new mobile number {new_mobile_number} has been saved.")

            await update.message.reply_text(TRANSLATIONS["mobile_number_saved"].format(new_mobile_number=new_mobile_number))


            await ShowMyObject_based_on_mobile_number(new_mobile_number, update)
        

def generate_financial_status_message(code, deposit, debt):
    """
    Generates a financial status message based on deposit and debt values.
    """
    logger.info(f"debt: {debt}, deposit: {deposit}")

    if debt == 0 and deposit == 0:
        # Case 1: No debt, no deposit - we are good.
        return TRANSLATIONS["case_no_debt_no_deposit"].format(code=code)
    elif debt < 0 and deposit == 0:
        # Case 2: There is a debt, deposit is 0
        return TRANSLATIONS["case_debt_no_deposit"].format(code=code, debt=debt)
    elif debt == 0 and deposit > 0:
        # Case 3: Positive Deposit, no Debt
        return TRANSLATIONS["case_no_debt_with_deposit"].format(code=code, deposit=deposit)
    elif debt > 0 and deposit > 0:
        # Case 4: Positive Deposit, Positive Debt
        return TRANSLATIONS["case_debt_and_deposit"].format(code=code, deposit=deposit, debt=debt)



    # if debt == 0 and deposit == 0:
    #     # Case 1: n dept , no deposit - we r good.
        
    #             return f"{code} DEBT is 0,and deposit is 0, meaning all payments are up to date. Thanks for your timely payments!"
    # elif debt < 0 and deposit == 0:
    #     # Case 2: there is a debt in this case we will always exepct deposit -0 
    #     return f"{code} You have debt , amount debt is :  {debt} . Please do payments ASAP."
    # elif debt == 0 and deposit > 0:
    #     # Case 4: Positive Deposit, no Debt
    #     return f"{code} You have deposit, deposit  amount = {deposit}. Thanks for closing payment on time."
    # elif debt > 0 and deposit > 0:
    #     # Case 4: Positive Deposit, Positive Debt
    #     return f"{code} You have deposit amount = {deposit}.  You have debt amount = {debt}" #i don't think these will be a case 
        

# async def handle_mobile_number(update, context):
#     """
#     Handles the mobile number input to fetch user objects and display dynamic buttons.
#     """
#     telegram_id = update.message.from_user.id
#     mobile_number = update.message.text

#     # Normalize mobile number
#     if mobile_number.startswith("+"):
#         mobile_number = mobile_number[1:]  # Remove '+'
#     elif mobile_number.startswith("0"):
#         mobile_number = "374" + mobile_number[1:]  # Replace '0' with '374'

#     # Fetch properties
#     validation_response = fetch_customer_properties(mobile_number)
    
#     if validation_response and "customerProperties" in validation_response:
#         properties = validation_response["customerProperties"]
        
#         # Generate buttons and status messages for each object
#         keyboard = []
#         status_messages = []
#         for prop in properties:
#             code = prop["code"]
#             obj_type = prop["type"]

#             # Fetch detailed property info for deposit and debt
#             details = fetch_property_details(code)
#             if details:
#                 deposit = details.get("deposit", 0)
#                 debt = details.get("debt", 0)

#                 # Generate financial status message
#                 status_message = generate_financial_status_message(code, deposit, debt)
#                 status_messages.append(status_message)

#                 # Log the status message for debugging
#                 logger.info(f"Generated status message for {code}: {status_message}")

#                 # Add button for object
#                 button_text = f"{code} ({obj_type})"
#                 keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_details_{code}")])

#         # Send status messages to user
#         if status_messages:
#             await update.message.reply_text("\n".join(status_messages))

#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await update.message.reply_text(
#             "We found objects assigned to you. Select one to view details:",
#             reply_markup=reply_markup
#         )

#     else:
#         await update.message.reply_text("No objects found linked to this mobile number.")



async def handle_object_selection(update, context):
    """
    Handles the selection of an object to display its payment history.
    """
    query = update.callback_query
    await query.answer()

    # Extract object code from callback data
    callback_data = query.data
    if callback_data.startswith("view_details_"):
        code = callback_data.replace("view_details_", "")

        logger.info(f"Fetching payment history for object code: {code}")

        # Fetch payment history
        details = fetch_property_details(code)

        if details and isinstance(details, dict):
            logger.info(f"Property details retrieved successfully for code {code}: {details}")

            transactions = details.get("transactionsPayInfo", [])
            
            if transactions:
                # Format the payment history
                history = "\n".join([
                    f"{trans['payedDate']}: {trans['payedAmount']}" for trans in transactions
                ])
                message = f"Payment History for {code}:\n{history}"
            else:
                message = f"Payment History for {code}: No transactions found."

            await query.edit_message_text(message)
        else:
            logger.error(f"Failed to fetch property details for code {code}. Response: {details}")
            # await query.edit_message_text("Failed to fetch property details. Please try again later.")
            await update.message.reply_text(TRANSLATIONS["fetch_details_failed"])


# ===========

async def handle_mobile_number(update, context):
    """
    Handles the mobile number input to fetch user objects and display dynamic buttons.
    """
    telegram_id = update.message.from_user.id

    # Check if user exists in the database
    user = check_user_exists(telegram_id)

    if user:
        # Existing user
        stored_mobile_number = user.get("mobile_number")
        await update.message.reply_text(
            f"Hey, I remember you! Last time, you used the following mobile number: {stored_mobile_number}.\n"
            "If your mobile number has changed, enter a new one. Otherwise, here are your objects.\n"
            "format -> +374xxxxxxxx կամ 0xxxxxxxx"
        )

        # Wait for new input or use stored mobile number
        context.user_data["mobile_number"] = stored_mobile_number
        # If user responds with a new number, it will be handled via process_mobile_number
    else:
        # New user prompt
        await update.message.reply_text(
            "Խնդրում ենք մուտքագրեք ձեր հեռախոսահամարը, որը գրանված է համատիրության գրանցամատյանում այս ֆորմատով՝ +374xxxxxxxx կամ 0xxxxxxxx\n"
            "to test use - < 37491995901 > <37494777513> < 37455024479 > < 37494555585 >"
        )


async def process_mobile_number(update, context):
    """
    Process the mobile number provided by the user.
    """
    telegram_id = update.message.from_user.id
    mobile_number = update.message.text

    # Normalize mobile number
    if mobile_number.startswith("+"):
        mobile_number = mobile_number[1:]  # Remove '+'
    elif mobile_number.startswith("0"):
        mobile_number = "374" + mobile_number[1:]  # Replace '0' with '374'

    # Save or update the user's mobile number in the database
    save_user(telegram_id, mobile_number)
    context.user_data["mobile_number"] = mobile_number

    # Fetch properties
    validation_response = fetch_customer_properties(mobile_number)

    if validation_response and "customerProperties" in validation_response:
        properties = validation_response["customerProperties"]

        # Generate buttons and status messages for each object
        keyboard = []
        status_messages = []
        for prop in properties:
            code = prop["code"]
            obj_type = prop["type"]

            # Fetch detailed property info for deposit and debt
            details = fetch_property_details(code)
            if details:
                deposit = details.get("deposit", 0)
                debt = details.get("debt", 0)

                # Generate financial status message
                status_message = generate_financial_status_message(code, deposit, debt)
                status_messages.append(status_message)

                # Log the status message for debugging
                logger.info(f"Generated status message for {code}: {status_message}")

                # Add button for object
                button_text = f"{code} ({obj_type})"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_details_{code}")])

        # Send status messages to user
        if status_messages:
            await update.message.reply_text("\n".join(status_messages))

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            TRANSLATIONS["found_objects"]
,
            reply_markup=reply_markup
        )

    else:
        await update.message.reply_text(TRANSLATIONS["no_objects_found"])





async def ShowMyObject_based_on_mobile_number(mobile_number_param, update):
    """
    Process the mobile number provided by the user and show their objects.
    """
    # Normalize mobile number
    if mobile_number_param.startswith("+"):
        mobile_number_param = mobile_number_param[1:]  # Remove '+'
    elif mobile_number_param.startswith("0"):
        mobile_number_param = "374" + mobile_number_param[1:]  # Replace '0' with '374'

    # Fetch properties
    validation_response = fetch_customer_properties(mobile_number_param)

    if validation_response and "customerProperties" in validation_response:
        properties = validation_response["customerProperties"]

        # Generate buttons and status messages for each object
        keyboard = []
        status_messages = []
        for prop in properties:
            code = prop["code"]
            obj_type = prop["type"]

            # Fetch detailed property info for deposit and debt
            details = fetch_property_details(code)
            if details:
                deposit = details.get("deposit", 0)
                debt = details.get("debt", 0)

                # Generate financial status message
                status_message = generate_financial_status_message(code, deposit, debt)
                status_messages.append(status_message)

                # Log the status message for debugging
                logger.info(f"Generated status message for {code}: {status_message}")

                # Add button for object
                button_text = f"{code} ({obj_type})"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_details_{code}")])

        # Add Change_Assosiate_mobile button
        keyboard.append([InlineKeyboardButton(TRANSLATIONS["change_mobile"], callback_data="Change_Assosiate_mobile")])

        # Send status messages to user
        if status_messages:
            if update.callback_query:
                # Handle callback query context
                await update.callback_query.message.reply_text("\n".join(status_messages))
            else:
                # Handle text message context
                await update.message.reply_text("\n".join(status_messages))

        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.message.reply_text(
                TRANSLATIONS["found_objects"],
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                TRANSLATIONS["found_objects"],
                reply_markup=reply_markup
            )
    else:
        # No objects found, prompt user to change mobile number
        keyboard = [[InlineKeyboardButton(TRANSLATIONS["change_mobile"], callback_data="Change_Assosiate_mobile")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.message.reply_text(
                TRANSLATIONS["ask_mobile_number"],
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                TRANSLATIONS["ask_mobile_number"],
                reply_markup=reply_markup
            )
