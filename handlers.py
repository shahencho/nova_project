from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from menu_helpers import get_object_menu, get_flat_building_menu
from api_helpers import fetch_deposit_and_debt_from_api
from database_operations import check_user_exists
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
        await update.message.reply_text("Welcome! Please enter your mobile number:")

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
        building = query.data.replace("building_flat_", "").replace("/", "_")
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
        
        