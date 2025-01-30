from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from handlers import start,handle_text
from settings import BOT_TOKEN
import logging

 
 
from  database_operations import initiate_connection


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

import logging
from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from settings import BOT_TOKEN  # Replace with your actual token or import from settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the conversation states
LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4 = range(4)

# Function to create navigation buttons
def get_navigation_buttons(level):
    buttons = []
    if level > LEVEL_1:
        buttons.append([InlineKeyboardButton("Previous Level", callback_data=f"prev_{level}")])
    if level < LEVEL_4:
        buttons.append([InlineKeyboardButton("Next Level", callback_data=f"next_{level}")])
    return InlineKeyboardMarkup(buttons)

# Start the conversation
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Welcome! Let's begin. Please provide input for Level 1:",
        reply_markup=ReplyKeyboardRemove()
    )
    return LEVEL_1

# Handle Level 1 input
async def level_1(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    context.user_data['level_1_input'] = user_input  # Save input
    await update.message.reply_text(
        f"Level 1 input received: {user_input}\nNow, provide input for Level 2:",
        reply_markup=get_navigation_buttons(LEVEL_1)
    )
    return LEVEL_2

# Handle Level 2 input
async def level_2(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    context.user_data['level_2_input'] = user_input  # Save input
    await update.message.reply_text(
        f"Level 2 input received: {user_input}\nNow, provide input for Level 3:",
        reply_markup=get_navigation_buttons(LEVEL_2)
    )
    return LEVEL_3

# Handle Level 3 input
async def level_3(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    context.user_data['level_3_input'] = user_input  # Save input
    await update.message.reply_text(
        f"Level 3 input received: {user_input}\nFinally, provide input for Level 4:",
        reply_markup=get_navigation_buttons(LEVEL_3)
    )
    return LEVEL_4

# Handle Level 4 input and summarize
async def level_4(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    context.user_data['level_4_input'] = user_input  # Save input
    
    # Summarize the collected data
    summary = (
        f"Here's what you've entered:\n"
        f"Level 1: {context.user_data['level_1_input']}\n"
        f"Level 2: {context.user_data['level_2_input']}\n"
        f"Level 3: {context.user_data['level_3_input']}\n"
        f"Level 4: {context.user_data['level_4_input']}\n"
    )
    await update.message.reply_text(summary + "Thank you!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Handle navigation button presses
async def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    # Extract the level from the callback data
    action, level = query.data.split("_")
    level = int(level)

    if action == "next":
        # Ask for input for the next level
        if level == LEVEL_1:
            await query.message.reply_text("Please provide input for Level 2:")
            return LEVEL_2
        elif level == LEVEL_2:
            await query.message.reply_text("Please provide input for Level 3:")
            return LEVEL_3
        elif level == LEVEL_3:
            await query.message.reply_text("Please provide input for Level 4:")
            return LEVEL_4
    elif action == "prev":
        # Go back to the previous level
        if level == LEVEL_2:
            await query.message.reply_text("Please provide input for Level 1:")
            return LEVEL_1
        elif level == LEVEL_3:
            await query.message.reply_text("Please provide input for Level 2:")
            return LEVEL_2
        elif level == LEVEL_4:
            await query.message.reply_text("Please provide input for Level 3:")
            return LEVEL_3

    return ConversationHandler.END

# Cancel the conversation
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Conversation canceled. Type /start to try again.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Main function to set up the bot
def main():
    logger.info("Starting bot application...")
    
    # Create the application instance
    application = Application.builder().token(BOT_TOKEN).build()

    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LEVEL_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, level_1)],
            LEVEL_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, level_2)],
            LEVEL_3: [MessageHandler(filters.TEXT & ~filters.COMMAND, level_3)],
            LEVEL_4: [MessageHandler(filters.TEXT & ~filters.COMMAND, level_4)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    # Add the button handler
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot using polling
    application.run_polling()
    Add the conversation handler to the application
if __name__ == "__main__":
    main()
