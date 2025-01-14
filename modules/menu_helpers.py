from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging

logger = logging.getLogger(__name__)

def get_object_menu():
    logger.info("Generating object selection menu.")
    keyboard = [
        [InlineKeyboardButton("Flat", callback_data="object_flat")],
        [InlineKeyboardButton("Public Space", callback_data="object_public_space")],
        [InlineKeyboardButton("Parking", callback_data="object_parking")],
        [InlineKeyboardButton("Uniq Payment Code", callback_data="object_uniq_payment_code")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_flat_building_menu():
    logger.info("Generating building menu for Flat.")
    buildings = ["46", "46/1", "48", "50", "52", "52/1"]
    keyboard = [[InlineKeyboardButton(building, callback_data=f"building_flat_{building}")] for building in buildings]
    return InlineKeyboardMarkup(keyboard)

def get_public_space_building_menu():
    logger.info("Generating building menu for Public Space.")
    buildings = ["46", "48", "50", "50/1", "52"]
    keyboard = [[InlineKeyboardButton(building, callback_data=f"building_public_space_{building}")] for building in buildings]
    return InlineKeyboardMarkup(keyboard)

def get_parking_building_menu():
    logger.info("Generating building menu for Parking.")
    buildings = ["46", "46/1", "48", "50", "50/1", "52", "52/1"]
    keyboard = [[InlineKeyboardButton(building, callback_data=f"building_parking_{building}")] for building in buildings]
    return InlineKeyboardMarkup(keyboard)
