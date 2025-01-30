import schedule
import time
import datetime
import logging
from database_operations import initiate_connection  # Reuse your DB functions
from api_helpers import fetch_deposit_and_debt_from_api  # Reuse API helpers
from telegram import Bot
from reminder_settings import REMINDER_SETTINGS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token (use your existing token)
BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=BOT_TOKEN)

def should_send_reminder(today):
    """Check if a reminder should be sent based on the schedule."""
    start_date = REMINDER_SETTINGS["default_date"]
    repeat_days = REMINDER_SETTINGS["when_to_repeat"]

    # Calculate reminder dates
    valid_dates = [start_date + i * repeat_days for i in range((31 - start_date) // repeat_days + 1)]
    return today.day in valid_dates

def send_reminders():
    """Send reminders to users with outstanding debts."""
    now = datetime.datetime.now()
    if not should_send_reminder(now):
        logger.info(f"No reminders scheduled for today ({now.date()}).")
        return

    # Fetch users from the database
    connection = initiate_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        logger.info("Fetching users from the database...")
        cursor.execute("SELECT telegram_id, mobile_number FROM user_table_inova_new")
        users = cursor.fetchall()

        for user in users:
            telegram_id = user["telegram_id"]
            mobile_number = user["mobile_number"]

            logger.info(f"Processing user: {telegram_id}, {mobile_number}")

            # Fetch object codes linked to the user
            # Assume fetch_customer_properties is already defined
            properties = fetch_customer_properties(mobile_number)
            if not properties or "customerProperties" not in properties:
                logger.warning(f"No properties found for user {telegram_id}. Skipping...")
                continue

            for obj in properties["customerProperties"]:
                code = obj["code"]
                obj_type = obj["type"]

                # Check for outstanding debt
                deposit, debt = fetch_deposit_and_debt_from_api(code)
                if debt and debt > 0:
                    # Send reminder notification
                    message = f"Dear customer, please close your debt: {debt} (Code: {code}, Type: {obj_type})."
                    bot.send_message(chat_id=telegram_id, text=message)
                    logger.info(f"Sent reminder to {telegram_id}: {message}")
                else:
                    logger.info(f"No outstanding debt for code {code}.")
    except Exception as e:
        logger.error(f"Error while processing reminders: {e}")
    finally:
        cursor.close()
        connection.close()

def run_scheduler():
    """Schedule the reminder task."""
    schedule_time = REMINDER_SETTINGS["time_to_send_notification"]
    schedule.every().day.at(schedule_time).do(send_reminders)

    logger.info(f"Reminder service scheduled at {schedule_time} daily.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()
