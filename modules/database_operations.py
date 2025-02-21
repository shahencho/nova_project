# database_operations.py
import mysql.connector
import logging
from api_helpers import fetch_customer_properties

# Configure logging
logger = logging.getLogger(__name__)

# Database connection
# def initiate_connection():
  #   logger.info("Initiating database connection...")
    # mydb = mysql.connector.connect(
      #   host='localhost',
        # user='shahencho',
        # password='Myelea82!',
        # database='shahencho_mydatabase'
    # )
    # return mydb

# def initiate_connection():
#     mydb = mysql.connector.connect(
#     host='localhost',
#     user='shahencho',
#     password='Dielea82!Ocean',
#     database='shahencho_mydatabase'
#     )
#     return mydb


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
def update_user_details(telegram_id, obj_type=None, unique_payment_code=None, mobile_number=None):
    """
    Updates user details in the database. Updates only fields provided as non-None values.
    """
    logger.info(f"Updating user details: telegram_id={telegram_id}, obj_type={obj_type}, unique_payment_code={unique_payment_code}, mobile_number={mobile_number}")
    mydb = initiate_connection()
    cursor = mydb.cursor()
    try:
        # Build the dynamic update query
        fields = []
        values = []
        if obj_type is not None:
            fields.append("obj_type = %s")
            values.append(obj_type)
        if unique_payment_code is not None:
            fields.append("unique_payment_code = %s")
            values.append(unique_payment_code)
        if mobile_number is not None:
            fields.append("mobile_number = %s")
            values.append(mobile_number)
        
        if fields:
            query = f"UPDATE user_table_inova_new SET {', '.join(fields)} WHERE telegram_id = %s"
            values.append(telegram_id)
            cursor.execute(query, values)
            mydb.commit()
            logger.info("User details updated successfully.")
    finally:
        cursor.close()
        mydb.close()




def save_user(telegram_id, mobile_number):
    """
    Saves or updates a user's details in the database.
    """
    # Normalize the mobile number
    if mobile_number.startswith("+"):
        mobile_number = mobile_number[1:]  # Remove '+'
    elif mobile_number.startswith("0"):
        mobile_number = "374" + mobile_number[1:]  # Replace '0' with '374'

    connection = initiate_connection()
    cursor = connection.cursor()

    # Check if the user already exists
    query = "SELECT * FROM user_table_inova_new WHERE telegram_id = %s"
    cursor.execute(query, (telegram_id,))
    user = cursor.fetchone()

    if user:
        # Update existing user
        query = """
        UPDATE user_table_inova_new
        SET mobile_number = %s
        WHERE telegram_id = %s
        """
        cursor.execute(query, (mobile_number, telegram_id))
        logger.info(f"Updated mobile number for telegram_id {telegram_id}: {mobile_number}")
    else:
        # Insert new user
        query = """
        INSERT INTO user_table_inova_new (telegram_id, mobile_number)
        VALUES (%s, %s)
        """
        cursor.execute(query, (telegram_id, mobile_number))
        logger.info(f"Saved new user with telegram_id {telegram_id} and mobile_number {mobile_number}")

    connection.commit()
    cursor.close()
    connection.close()


async def validate_and_fetch_mobile_number(new_mobile_number):
    """
    Validates and normalizes a mobile number, then checks its validity via the API.
    Returns True if valid and API call is successful, otherwise returns False.
    """
    # Normalize mobile number
    if new_mobile_number.startswith("+"):
        new_mobile_number = new_mobile_number[1:]  # Remove '+'
    elif new_mobile_number.startswith("0"):
        new_mobile_number = "374" + new_mobile_number[1:]  # Replace '0' with '374'
    
    logger.info(f"Normalized mobile number: {new_mobile_number}")

    # # Validate mobile number format
    # if not new_mobile_number.isdigit() or not new_mobile_number.startswith("374") or len(new_mobile_number) != 12:
    #     logger.warning(f"Invalid mobile number after normalization: {new_mobile_number}")
    #     return False

    # API call to validate mobile number
    validation_response = fetch_customer_properties(new_mobile_number)

    logger.info(logger.info(f"validation_response >>>>>>>>>  {validation_response}  "))    

    if validation_response and "customerProperties" in validation_response:
        logger.info(f"Mobile number {new_mobile_number} is valid and associated with properties.")
        return True

    logger.warning(f"Mobile number {new_mobile_number} is not associated with any properties.")
    return False
