# database_operations.py
import mysql.connector
import logging

# Configure logging
logger = logging.getLogger(__name__)

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



def save_user(telegram_id, mobile_number):
    connection = initiate_connection()
    cursor = connection.cursor()

    # Check if user already exists
    query = "SELECT * FROM user_table_inova_new WHERE telegram_id = %s"
    cursor.execute(query, (telegram_id,))
    user = cursor.fetchone()

    if user:
        logger.info(f"User with telegram_id {telegram_id} already exists in the database.")
    else:
        # Insert new user
        query = """
        INSERT INTO user_table_inova_new (telegram_id, mobile_number)
        VALUES (%s, %s)
        """
        cursor.execute(query, (telegram_id, mobile_number))
        connection.commit()
        logger.info(f"New user with telegram_id {telegram_id} has been added to the database.")

    cursor.close()
    connection.close()