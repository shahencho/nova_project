import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    ContextTypes
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "7576350206:AAFfR-I6r4tfaP6m2yQBWGsrAPMpLQt9CL8"

# Function to send periodic messages (placeholder for future implementation)
async def send_periodic_message():
    while True:
        time.sleep(3600)  # Wait for 1 hour (adjust as needed)
        logger.info("Periodic message thread is running.")

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined building numbers
BUILDINGS_FLAT = ["46", "46/1", "48", "50", "52", "52/1"]
BUILDINGS_PUBLIC_SPACE = ["46", "48", "50", "50/1", "52"]
BUILDINGS_PARKING = ["46", "46/1", "48", "50", "50/1", "52", "52/1"]

# Temporary storage for user selections
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import mysql.connector
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import mysql.connector
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined building numbers
BUILDINGS_FLAT = ["46", "46/1", "48", "50", "52", "52/1"]
BUILDINGS_PUBLIC_SPACE = ["46", "48", "50", "50/1", "52"]
BUILDINGS_PARKING = ["46", "46/1", "48", "50", "50/1", "52", "52/1"]

# Temporary storage for user selections
user_data = {}

# Database connection
def initiate_connection():
    logger.info("Initiating database connection...")
    mydb = mysql.connector.connect(
        host='localhost',
        user='shahencho',
        password='Myelea82!',
        database='shahencho_mydatabase'
    )
    return mydb

# Check if user exists in the database
def check_user_exists(telegram_id, mobile_number=None):
    logger.info(f"Checking if user exists: telegram_id={telegram_id}, mobile_number={mobile_number}")
    mydb = initiate_connection()
    cursor = mydb.cursor(dictionary=True)
    try:
        if mobile_number:
            query = "SELECT * FROM user_table_inova_new WHERE telegram_id = %s OR mobile_number = %s"
            cursor.execute(query, (telegram_id, mobile_number))
        else:
            query = "SELECT * FROM user_table_inova_new WHERE telegram_id = %s"
            cursor.execute(query, (telegram_id,))
        result = cursor.fetchone()
        logger.info(f"User lookup result: {result}")
        return result
    finally:
        cursor.close()
        mydb.close()

# Add or update user details in the database
def update_user_details(telegram_id, obj_type, unique_payment_code):
    logger.info(f"Updating user details: telegram_id={telegram_id}, obj_type={obj_type}, unique_payment_code={unique_payment_code}")
    mydb = initiate_connection()
    cursor = mydb.cursor()
    try:
        query = "UPDATE user_table_inova_new SET obj_type = %s, unique_payment_code = %s WHERE telegram_id = %s"
        cursor.execute(query, (obj_type, unique_payment_code, telegram_id))
        mydb.commit()
        logger.info("User details updated successfully.")
    finally:
        cursor.close()
        mydb.close()

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    logger.info(f"Received /start command from telegram_id={telegram_id}")
    user = check_user_exists(telegram_id)

    if user:
        logger.info("User found in database. Proceeding to main menu.")
        await update.message.reply_text("Welcome back! You are already registered.")
        reply_markup = get_object_menu()
        await update.message.reply_text("Please choose your object:", reply_markup=reply_markup)
    else:
        logger.info("User not found. Asking for mobile number.")
        user_data[telegram_id] = {"state": "ask_mobile"}
        await update.message.reply_text("Welcome! Please enter your mobile number to register:")

# Message handler for text input
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    logger.info(f"Received text message from telegram_id={telegram_id}")

    if telegram_id in user_data:
        state = user_data[telegram_id].get("state")
        if state == "entering_flat":
            flat_number = update.message.text
            building = user_data[telegram_id]["building"]
            logger.info(f"User entered flat number: {flat_number} for building: {building}")

            # Generate unique payment code
            unique_payment_code = f"flat_building_{building}_flat_{flat_number}"
            update_user_details(telegram_id, "flat", unique_payment_code)

            await update.message.reply_text(f"Your payment for Building {building} selected. Flat number: {flat_number} is $1000")

            # Clear user state after completing the process
            del user_data[telegram_id]

            # Optionally, show main menu again
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        elif state == "entering_public_space":
            public_space_id = update.message.text
            building = user_data[telegram_id]["building"]
            logger.info(f"User entered public space ID: {public_space_id} for building: {building}")
            await update.message.reply_text(f"Your payment for Building {building} selected. Public space ID: {public_space_id} is $1000")

            # Clear user state after completing the process
            del user_data[telegram_id]

            # Optionally, show main menu again
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        elif state == "entering_parking":
            parking_id = update.message.text
            building = user_data[telegram_id]["building"]
            logger.info(f"User entered parking ID: {parking_id} for building: {building}")
            await update.message.reply_text(f"Your payment for Building {building} selected. Parking ID: {parking_id} is $1000")

            # Clear user state after completing the process
            del user_data[telegram_id]

            # Optionally, show main menu again
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        elif state == "entering_unique_code":
            unique_code = update.message.text
            logger.info(f"User entered unique payment code: {unique_code}")
            await update.message.reply_text(f"Your payment for the entered unique payment code {unique_code} is $1000")

            # Clear user state after completing the process
            del user_data[telegram_id]

            # Optionally, show main menu again
            reply_markup = get_object_menu()
            await update.message.reply_text("Do you want to look at other information?", reply_markup=reply_markup)

        else:
            logger.info("User is in an unexpected state.")
            await update.message.reply_text("Please complete the current process or use /start to begin.")
    else:
        logger.info("User is not in registration state. Asking to use /start.")
        await update.message.reply_text("Please start by using /start to begin.")

# Handle callback queries
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    # Log callback data for debugging
    logger.info(f"Callback data received: {query.data}")

    # Handle object selection
    if query.data == "object_flat":
        logger.info("User selected Flat.")
        user_data[query.from_user.id] = {"state": "selecting_building", "object": "flat"}
        await query.edit_message_text("You selected Flat. Please choose your building:")
        keyboard = [[InlineKeyboardButton(building, callback_data=f"building_flat_{building}")] for building in BUILDINGS_FLAT]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup)

    elif query.data == "object_public_space":
        logger.info("User selected Public Space.")
        user_data[query.from_user.id] = {"state": "selecting_building", "object": "public_space"}
        await query.edit_message_text("You selected Public Space. Please choose your building:")
        keyboard = [[InlineKeyboardButton(building, callback_data=f"building_public_space_{building}")] for building in BUILDINGS_PUBLIC_SPACE]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup)

    elif query.data == "object_parking":
        logger.info("User selected Parking.")
        user_data[query.from_user.id] = {"state": "selecting_building", "object": "parking"}
        await query.edit_message_text("You selected Parking. Please choose your building:")
        keyboard = [[InlineKeyboardButton(building, callback_data=f"building_parking_{building}")] for building in BUILDINGS_PARKING]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup)

    elif query.data == "object_uniq_payment_code":
        logger.info("User selected Uniq Payment Code.")
        user_data[query.from_user.id] = {"state": "entering_unique_code"}
        await query.edit_message_text("You selected Uniq Payment Code. Please enter your unique code:")

    # Handle building selection
    elif query.data.startswith("building_flat_"):
        building = query.data.replace("building_flat_", "")
        logger.info(f"User selected building: {building}")
        user_data[query.from_user.id] = {"state": "entering_flat", "building": building, "object": "flat"}
        await query.edit_message_text(f"You selected Building {building}. Please enter your flat number:")

    elif query.data.startswith("building_public_space_"):
        building = query.data.replace("building_public_space_", "")
        logger.info(f"User selected Public Space building: {building}")
        user_data[query.from_user.id] = {"state": "entering_public_space", "building": building, "object": "public_space"}
        await query.edit_message_text(f"You selected Building {building}. Please enter the public space ID:")

    elif query.data.startswith("building_parking_"):
        building = query.data.replace("building_parking_", "")
        logger.info(f"User selected Parking building: {building}")
        user_data[query.from_user.id] = {"state": "entering_parking", "building": building, "object": "parking"}
        await query.edit_message_text(f"You selected Building {building}. Please enter your parking ID:")

# Display object selection menu
def get_object_menu():
    logger.info("Generating object selection menu.")
    keyboard = [
        [InlineKeyboardButton("Flat", callback_data="object_flat")],
        [InlineKeyboardButton("Public Space", callback_data="object_public_space")],
        [InlineKeyboardButton("Parking", callback_data="object_parking")],
        [InlineKeyboardButton("Uniq Payment Code", callback_data="object_uniq_payment_code")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Main function
def main():
    logger.info("Starting bot application...")
    # Initialize the application
    application = Application.builder().token("7576350206:AAFfR-I6r4tfaP6m2yQBWGsrAPMpLQt9CL8").build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
