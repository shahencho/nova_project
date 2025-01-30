from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from translations import TRANSLATIONS  # Import the translations
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import KeyboardButton, ReplyKeyboardMarkup
import time


logger = logging.getLogger(__name__)

def Change_Assosiate_mobile():
    logger.info("Change_Assosiate_mobile .")
    keyboard = [
        [InlineKeyboardButton("Change_Assosiate_mobile", callback_data="Change_Assosiate_mobile")],

    ]
    return InlineKeyboardMarkup(keyboard)

    
# def get_main_menu():
#     logger.info("Generating main menu with KeyboardButton.")
#     keyboard = [
#         [KeyboardButton(TRANSLATIONS["yes_show_objects"])],
#         [KeyboardButton(TRANSLATIONS["change_mobile"])],
#         # [KeyboardButton("contact_with_us")]
        
#     ]
    
#     return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# def get_main_menu():
#     logger.info("Generating main menu with InlineKeyboardButton.")
#     keyboard = [
#         [InlineKeyboardButton("Show Objects", callback_data="show_objects")],
#         [InlineKeyboardButton("Change Mobile", callback_data="change_mobile")],
#         [InlineKeyboardButton("View Report", url="https://docs.google.com")]
#     ]
#     return InlineKeyboardMarkup(keyboard)




def get_main_menu():
    logger.info("Generating main menu with KeyboardButton.")
    GOOGLE_DOC_LINK = "https://docs.google.com/document/d/your_google_doc_id/view"
    keyboard = [
        [KeyboardButton(TRANSLATIONS["yes_show_objects"])],
        [KeyboardButton(TRANSLATIONS["change_mobile"])],
        [InlineKeyboardButton("View Report", url=GOOGLE_DOC_LINK)]  # New button added
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)



async def display_blady_button(update: Update):
    """
    Display a button with the name "Blady."
    """
    start_time = time.time()
    logger.info("Displaying 'Blady' button.")
    
     
    keyboard = [[KeyboardButton(TRANSLATIONS["Blady"])]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Սեղմել ոե:", reply_markup=reply_markup)

    logger.info(f"Displayed 'Blady' button in {time.time() - start_time:.2f} seconds")


    

    