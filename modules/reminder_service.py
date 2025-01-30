
from settings import BOT_TOKEN
import datetime
import logging
from database_operations import initiate_connection
from api_helpers import fetch_deposit_and_debt_from_api, fetch_customer_properties
from telegram import Bot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings for the reminder service
REMINDER_SETTINGS = {
    "default_date": 20,  # Day of the month to start validating
    "when_to_repeat": 2,  # Days between reminders
    "time_to_send_notification": "15:00",  # Time to send notifications
    "bot_token": BOT_TOKEN,  # Replace with your actual bot token
}


def should_send_reminder(today):
    """Check if a reminder should be sent based on the schedule."""
    start_date = REMINDER_SETTINGS["default_date"]
    repeat_days = REMINDER_SETTINGS["when_to_repeat"]

    # Calculate valid dates for reminders
    valid_dates = [start_date + i * repeat_days for i in range((31 - start_date) // repeat_days + 1)]
    return today.day in valid_dates


def fetch_users_with_debt():
    """Fetch users with outstanding debt from the database."""
    connection = initiate_connection()
    cursor = connection.cursor(dictionary=True)
    users_with_debt = []

    try:
        logger.info("Fetching users from the database...")
        cursor.execute("SELECT telegram_id, mobile_number FROM user_table_inova_new")
        users = cursor.fetchall()

        for user in users:
            telegram_id = user["telegram_id"]
            mobile_number = user["mobile_number"]

            # Fetch object codes for the user
            properties = fetch_customer_properties(mobile_number)
            if not properties or "customerProperties" not in properties:
                continue

            # Check each object for outstanding debt
            for obj in properties["customerProperties"]:
                code = obj["code"]
                debt = fetch_deposit_and_debt_from_api(code)[1]  # Get debt
                if debt and debt > 0:
                    users_with_debt.append((telegram_id, code, debt))
    except Exception as e:
        logger.error(f"Error fetching users with debt: {e}")
    finally:
        cursor.close()
        connection.close()

    return users_with_debt


def send_notifications(users_with_debt):
    """Send reminders to users with outstanding debts."""
    bot = Bot(token=REMINDER_SETTINGS["bot_token"])

    for telegram_id, code, debt in users_with_debt:
        try:
            message = f"Dear customer, please close your debt: {debt} (Code: {code})."
            bot.send_message(chat_id=telegram_id, text=message)
            logger.info(f"Sent reminder to {telegram_id}: {message}")
        except Exception as e:
            logger.error(f"Failed to send reminder to {telegram_id}: {e}")


def main():
    """Main function to run the reminder service."""
    now = datetime.datetime.now()

    if should_send_reminder(now):
        logger.info("Starting the reminder service...")
        users_with_debt = fetch_users_with_debt()
        send_notifications(users_with_debt)
        logger.info("Reminder service completed.")
    else:
        logger.info("No reminders scheduled for today.")


if __name__ == "__main__":
    main()
