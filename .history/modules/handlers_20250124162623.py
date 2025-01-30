from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from api_helpers import fetch_deposit_and_debt_from_api, fetch_customer_properties, fetch_debt_for_code, fetch_property_details, generate_financial_status_message
from database_operations import check_user_exists, save_user, update_user_details, validate_and_fetch_mobile_number
from menu_helpers import Change_Assosiate_mobile, get_main_menu, display_blady_button
import logging
import time

from translations import TRANSLATIONS  # Import the translations

from telegram import KeyboardButton, ReplyKeyboardMarkup

from telegram.error import TimedOut  # Import the TimedOut exception
import httpx  # Import httpx if you're using it in your code

logger = logging.getLogger(__name__)

user_data = {}


import asyncio


logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    start_time = time.time()

    telegram_id = update.message.from_user.id

    if telegram_id not in user_data:
        user_data[telegram_id] = {"state": "step0_register_mobile"}  # Initialize user data
        logger.info(f"Initialized user data for telegram_id={telegram_id}")

    
    first_name = update.message.from_user.first_name  # Retrieve the user's first name
    logger.info(f"Received /start command from telegram_id={telegram_id} with name={first_name}")




    # Fetch and format the welcome message
    welcome_message = TRANSLATIONS["welcome_message"].format(name=first_name)

    user = check_user_exists(telegram_id)
    logger.info(f"User check returned: {user}")

    if user:
        logger.info("User found in database. Proceeding to main menu.")
        await update.message.reply_text(welcome_message)
        mobile_number = user.get("mobile_number", "Not available")

        x = fetch_customer_properties(mobile_number)
        logger.info(f"Customer properties fetched: {x}")

        # # Extract relevant properties
        # customer_properties = x.get("customerProperties", [])
        # property_details = "\n".join(
        #     [f"Code: {prop['code']}, Type: {prop['type']}" for prop in customer_properties]
        # )

        # # Combine the message
        # message = (

        #     f"{TRANSLATIONS['found_objects']}\n{property_details}"
        #     f"{TRANSLATIONS['mobile_saved_in_db_found']} : {mobile_number}\n\n"
            
        # )
        
        message1 = f"{TRANSLATIONS['mobile_saved_in_db_found']} : {mobile_number}\n\n"


        # await update.message.reply_text(message1)

        await display_properties(x, update)

        # await update.message.reply_text(message)

        reply_markup = get_main_menu()
        await update.message.reply_text(TRANSLATIONS["ask_to_view_details"], reply_markup=reply_markup)

        user_data[telegram_id] = {"state": "step1_mobile_register_succesfully"}  # Set state after successful registration

    else:
        user_data[telegram_id] = {"state": "step0_register_mobile"}  # Set state for first-time login
        await update.message.reply_text(welcome_message)
        await update.message.reply_text(TRANSLATIONS["ask_mobile_number"])
    
    logger.info(f"Completed /start command in {time.time() - start_time:.2f} seconds")


async def copy_of_ShowMyObject_based_on_mobile_number(mobile_number_param, update):
    """
    Process the mobile number provided by the user and show their objects using KeyboardButton.
    """
    # logger.info(f"Starting copy_of_ShowMyObject_based_on_mobile_number for {mobile_number_param}")

    start_time = time.time()
    logger.info(f"Starting copy_of_ShowMyObject_based_on_mobile_number for {mobile_number_param}")

    # Normalize mobile number
    if mobile_number_param.startswith("+"):
        mobile_number_param = mobile_number_param[1:]  # Remove '+'
    elif mobile_number_param.startswith("0"):
        mobile_number_param = "374" + mobile_number_param[1:]  # Replace '0' with '374'

    # Fetch properties
    validation_response = fetch_customer_properties(mobile_number_param)
    logger.info(f"Fetched properties for {mobile_number_param}: {validation_response}")

    if validation_response and "customerProperties" in validation_response:
        properties = validation_response["customerProperties"]

        # Generate buttons and status messages for each object
        keyboard = []
        status_messages = []
        for prop in properties:
            code = prop["code"]
            obj_type = prop["type"]
            apartment = prop["apartment"]
            flat_number = prop["number"]


            # Fetch detailed property info for deposit and debt
            details = fetch_property_details(code)
            logger.info(f"Fetched details for {code}: {details}")
            if details:
                deposit = details.get("deposit", 0)
                debt = details.get("debt", 0)
                


                current_code = details.get("code", 0)
                # Generate financial status message
                status_message = generate_financial_status_message(code, deposit, debt, apartment, obj_type, flat_number)
                status_messages.append(status_message)

                # Log the status message for debugging
                logger.info(f"Generated status message for {code}: {status_message}")

                # Add button for object
                button_text = f"{code} ({obj_type})"
                keyboard.append([KeyboardButton(button_text)])

        # Add Change_Assosiate_mobile button
        # keyboard.append([KeyboardButton(TRANSLATIONS["change_mobile"])]);
        # Add Back button

        keyboard.append([KeyboardButton(TRANSLATIONS["Back1"]), KeyboardButton(TRANSLATIONS["Refresh"])])

        
        

        # Send status messages to user
        if status_messages:
            await update.message.reply_text("\n".join(status_messages))

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        logger.info(f"Sending keyboard with objects: {keyboard}")
        await update.message.reply_text(
            TRANSLATIONS["found_objects"],
            reply_markup=reply_markup
        )

        # Update state and store previous state
        telegram_id = update.message.from_user.id
        user_data[telegram_id]["prev_state"] = user_data[telegram_id].get("state", "step1_mobile_register_succesfully") # can be from "back function "
        # user_data[telegram_id]["prev_state"] = user_data[telegram_id].get("state")# can be from "back function "
        user_data[telegram_id]["state"] = "step2_mobile_register_succesfully_show_my_objects"

        logger.info(f"\n in  copy_of_ShowMyObject_based_on_mobile_number  state =  {user_data[telegram_id]["state"] }and prev_state = {user_data[telegram_id]["prev_state"]}\n")

        logger.info(f"Completed copy_of_ShowMyObject_based_on_mobile_number in {time.time() - start_time:.2f} seconds")


    else:
        logger.warning(f"No objects found for {mobile_number_param}")
        # No objects found, prompt user to change mobile number
        keyboard = [[KeyboardButton(TRANSLATIONS["change_mobile"])]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            TRANSLATIONS["ask_mobile_number"],
            reply_markup=reply_markup
        )

async def show_payment_history(code, update):
    """
    Fetch and display the payment history for the selected object code.
    """
    logger.info(f"Fetching payment history for object code: {code}")

    # Fetch detailed property info
    details = fetch_property_details(code)
    logger.info(f"Fetched property details for {code}: {details}")

    if details and isinstance(details, dict):

        # Generate payment history
        transactions = details.get("transactionsPayInfo", [])
        if transactions:
            history = "\n".join([
                f"{trans['payedDate']}: {trans['payedAmount']}" for trans in transactions
            ])
            message = TRANSLATIONS["payment_history"].format(code=code, history=history)
        else:
            message = TRANSLATIONS["no_transactions"].format(code=code)

        # Send payment history to the user
        await update.message.reply_text(message)

        # Update user state to payment history
        telegram_id = update.message.from_user.id
        user_data[telegram_id]["prev_state"] = "step2_mobile_register_succesfully_show_my_objects"
        user_data[telegram_id]["state"] = "step4_mobile_register_succesfully_show_my_objects_show_payment_history"

        state1 = user_data[telegram_id].get("state")
        prev_state1 = user_data[telegram_id].get("prev_state")
        logger.info(f"printed from show payment history Current state: {state1}, Current prev_state: {prev_state1}")
    else:
        logger.error(f"Failed to fetch details for code: {code}")
        await update.message.reply_text(TRANSLATIONS["error_fetching_details"])

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    start_time = time.time()


    telegram_id = update.message.from_user.id
    user_input = update.message.text
    logger.info(f"Received text message from telegram_id={telegram_id}: {user_input}")

    state1 = user_data[telegram_id].get("state")
    prev_state1 = user_data[telegram_id].get("prev_state")
    logger.info(f"Current state: {state1}, Current prev_state: {prev_state1}")

    logger.info(f"Received text message from telegram_id={telegram_id}: {user_input}")


    if telegram_id in user_data:
        state = user_data[telegram_id].get("state")
        logger.info(f"Current state: {state}, User input: {user_input}")

        if user_input == TRANSLATIONS["change_mobile"]:
            logger.info(f"User selected 'change_mobile' for telegram_id={telegram_id}")
            await update.message.reply_text(TRANSLATIONS["ask_mobile_number"])
            # Update user state to ask for a mobile number
            user_data[telegram_id]["prev_state"] = user_data[telegram_id].get("state", "step0_register_mobile")
            user_data[telegram_id]["state"] = "step0_register_mobile"

            return

        elif user_input == "contact_with_us":
            logger.info(f"User selected 'contact_with_us' for telegram_id={telegram_id}")
            await update.message.reply_text("share with us your problem")
            # Update user state to ask for a mobile number
            user_data[telegram_id]["state"]= "contact_with_us"
            logger.info(f"save this info in db some time later!!!!!!!!!!!!s")
            await display_blady_button(update)
            return

        elif user_input == "View Report":
            GOOGLE_DOC_LINK = "https://docs.google.com/document/d/your_google_doc_id/view"
            await update.message.reply_text(f"You can view the report here: {GOOGLE_DOC_LINK}")
            return


        elif user_input == TRANSLATIONS["Refresh"]:
            logger.info(f"User selected 'Refresh' for telegram_id={telegram_id}")
            
            
            # await start(update, context)
            elif user_input == TRANSLATIONS["Refresh"]:
        logger.info(f"User selected 'Refresh' for telegram_id={telegram_id}")

        # Call the `initialize` function to handle expired or missing sessions
        user = await initialize(telegram_id)

        if user:
            logger.info("Reinitialization successful. Displaying refreshed menu.")
            # Reuse the existing logic to show the refreshed menu
            reply_markup = get_main_menu()
            await update.message.reply_text("Menu refreshed. Please choose an option:", reply_markup=reply_markup)
        else:
            logger.warning("Reinitialization failed. No user found.")
            await update.message.reply_text("Your session has expired. Please restart the bot by pressing /start.")




            #sss
            logger.info(f"User selected 'Refresh' for telegram_id={telegram_id}")
            user = check_user_exists(telegram_id)
            logger.info(f"User data fetched: {user}")
            if user and user.get("mobile_number"):
                mobile_number = user["mobile_number"]
                logger.info(f"Handling 'show_my_object' for mobile number: {mobile_number}")
                
                # Save previous state before calling the object list
                user_data[telegram_id]["prev_state"] = user_data[telegram_id].get("state", "step1_mobile_register_succesfully")
                await  copy_of_ShowMyObject_based_on_mobile_number(mobile_number, update)


            return



        elif user_input == TRANSLATIONS["yes_show_objects"]:
            logger.info(f"User selected 'yes_show_objects' for telegram_id={telegram_id}")
            user = check_user_exists(telegram_id)
            logger.info(f"User data fetched: {user}")
            if user and user.get("mobile_number"):
                mobile_number = user["mobile_number"]
                logger.info(f"Handling 'show_my_object' for mobile number: {mobile_number}")
                
                # Save previous state before calling the object list
                user_data[telegram_id]["prev_state"] = user_data[telegram_id].get("state", "step1_mobile_register_succesfully")
                await  copy_of_ShowMyObject_based_on_mobile_number(mobile_number, update)
               

            else:
                logger.warning(f"No mobile number found for user {telegram_id}")
                await update.message.reply_text(TRANSLATIONS["no_mobile_number_linked"])

         

        elif user_input.startswith("A-") or user_input.startswith("P-") or user_input.startswith("C-"):
            
            logger.info(f"User selected object: {user_input}")
            code = user_input.split()[0]  # Extract the code (e.g., "A-48-2") from the button text
            await show_payment_history(code, update)
             # Call the function to display "Blady" button
            await display_blady_button(update)
            logger.info(f"Processed object selection in {time.time() - start_time:.2f} seconds")

            return

            
        

        elif user_input == TRANSLATIONS["Back1"]:

            logger.info(f" user_input == Back1  Call Start!   ={user_input}")
                
            await start(update, context)
            return


        elif user_input == TRANSLATIONS["Blady"]:

            logger.info(f" user_input == Blady      ={user_input}")
                
            mobile_number = get_associated_with_this_telegram_id_mobile_number(telegram_id) #iif user came to back from step4 , his mobile number must be in db

            logger.info(f" user_input == BladyReturning to object list for mobile number: {mobile_number}")
            await copy_of_ShowMyObject_based_on_mobile_number(mobile_number, update)
           
            return
        
        elif user_input == "Back12222":
            prev_state = user_data[telegram_id].get("prev_state")
            if not prev_state:
                logger.warning(f"No previous state found for telegram_id={telegram_id}. Inferring fallback state.")
                # Infer fallback based on current state
                if state == "step4_mobile_register_succesfully_show_my_objects_show_payment_history":
                    prev_state = "step2_mobile_register_succesfully_show_my_objects"
                elif state == "step2_mobile_register_succesfully_show_my_objects":
                    prev_state = "step1_mobile_register_succesfully"
                else:
                    prev_state = "step0_register_mobile"  # Default fallback for unexpected cases

            logger.info(f"User selected 'Back' for telegram_id={telegram_id}")
            logger.info(f"prev_state ={prev_state} , current state is = {state}" )


            if prev_state == "step1_mobile_register_succesfully":
                logger.info(f" lets skip this now  prev_state== step1_mobile_register_succesfully")    
                # reply_markup = get_main_menu()
                # await update.message.reply_text(TRANSLATIONS["back_to_main_menu"], reply_markup=reply_markup)

            elif prev_state == "step2_mobile_register_succesfully_show_my_objects":
                # mobile_number = user_data[telegram_id].get("mobile_number")

                mobile_number = get_associated_with_this_telegram_id_mobile_number(telegram_id) #iif user came to back from step4 , his mobile number must be in db

                if mobile_number is None:
                    logger.info(f"something terrible went wrong. no mobile in db... {mobile_number}")    
                    return 


                logger.info(f"Returning to object list for mobile number: {mobile_number}")
                await copy_of_ShowMyObject_based_on_mobile_number(mobile_number, update)
                # get_step1_buttons()
                # reply_markup = get_main_menu()

            elif prev_state == "step4_mobile_register_succesfully_show_my_objects_show_payment_history":
                
                logger.info(f" Start called! prev_state == step4_mobile_register_succesfully_show_my_objects_show_payment_history step4_mobile_register_succesfully_show_my_objects_show_payment_history ={prev_state}")
                
                await start(update, context)
                # mobile_number = get_associated_with_this_telegram_id_mobile_number(telegram_id) #iif user came to back from step4 , his mobile number must be in db

                # if mobile_number is None:
                #     logger.info(f"something terrible went wrong. no mobile in db... {mobile_number}")    
                #     return 
                # logger.info(f"Returning to object list for mobile number: {mobile_number}")
                # await copy_of_ShowMyObject_based_on_mobile_number(mobile_number, update)..
                 # get_step1_buttons()
                # reply_markup = get_main_menu()
                # user_data[telegram_id]["state"] = prev_state



            
            return

       
        elif state == "step0_register_mobile" or user_input == TRANSLATIONS["change_mobile"]:
            logger.info(f"Handling mobile number input: State={state}, User Input={user_input}")

            new_mobile_number = user_input
            logger.info(f"User entered new mobile number: {new_mobile_number}")

            # Validate the mobile number

            # Validate the mobile number
            validation_result = await validate_mobile_number(new_mobile_number)

            if validation_result == "not_valid_format":
                await update.message.reply_text( "not_valid_format - > invalid_mobile_format +374xxxxxxxx or 0xxxxxxxx or 374xxxxxxxx ")
                return
            elif validation_result == "valid_not_registered_in_API":
                await update.message.reply_text(" mobile_not_registered_in_API enter what is registered in veracnund +374xxxxxxxx or 0xxxxxxxx or 374xxxxxxxx ")
                return

            # Save the mobile number if valid and registered
            save_user(telegram_id, new_mobile_number)
            logger.info(f"Mobile number {new_mobile_number} registered successfully for telegram_id={telegram_id}")


            # Transition to step1_mobile_register_succesfully
            user_data[telegram_id]["state"] = "step1_mobile_register_succesfully"
            await update.message.reply_text(TRANSLATIONS["mobile_number_saved"].format(new_mobile_number=new_mobile_number))
            
            await start(update, context)

            # reply_markup = get_main_menu()
            # await update.message.reply_text(TRANSLATIONS["choose_action"], reply_markup=reply_markup)
            # logger.info(f"Completed step0_register_mobile in {time.time() - start_time:.2f} seconds")

            return

        elif state == "step2_mobile_register_succesfully_show_my_objects":
            logger.info(f"we will catch this above ! User selected object we are in state == step2_mobile_register_succesfully_show_my_objects  ->: {user_input}")
            # code = user_input.split()[0]  # Extract code from button text
            # # user_data[telegram_id]["prev_state"] = "step2_mobile_register_succesfully_show_my_objects"
            # # user_data[telegram_id]["state"] = "step4_mobile_register_succesfully_show_my_objects_show_payment_history"
            # await show_payment_history(code, update)
            await update.message.reply_text("step1_mobile_register_succesfully Available options: choose buttons below ", reply_markup=reply_markup)


            return

            # Re-show the current menu (use the appropriate menu for the current state)
        elif state == "step1_mobile_register_succesfully":
            # reply_markup = get_main_menu()  # Reuse your existing menu function
            await update.message.reply_text("step1_mobile_register_succesfully Available options: choose buttons below ", reply_markup=reply_markup)
        elif state == "step2_mobile_register_succesfully_show_my_objects":
            reply_markup = get_objects_menu()  # Replace with your object menu function
            await update.message.reply_text("step2_mobile_register_succesfully_show_my_objects Available options: choose buttons below ", reply_markup=reply_markup)
        

        # elif state == "step4_mobile_register_succesfully_show_my_objects_show_payment_history":
        #     if user_input == "Back":
        #         logger.info(f"User selected 'Back' for telegram_id={telegram_id}")
        #         user_data[telegram_id]["state"] = "step2_mobile_register_succesfully_show_my_objects"
        #         mobile_number = user_data[telegram_id].get("mobile_number")
        #         await copy_of_ShowMyObject_based_on_mobile_number(mobile_number, update)
        #         return

        else:
            logger.warning(f"Unknown command or state for telegram_id={telegram_id}: {user_input}")
            await update.message.reply_text(TRANSLATIONS["unknown_command"])
    else:
        logger.warning(f"User data not found for telegram_id={telegram_id}")
        await update.message.reply_text(TRANSLATIONS["unknown_command"])

def get_associated_with_this_telegram_id_mobile_number(telegram_id):
    """
    Fetch the mobile number associated with the given Telegram ID.
    """
    logger.info(f"Fetching mobile number for telegram_id={telegram_id}")
    user = check_user_exists(telegram_id)
    if user:
        mobile_number = user.get("mobile_number")
        logger.info(f"Mobile number found for telegram_id={telegram_id}: {mobile_number}")
        return mobile_number
    logger.warning(f"No mobile number found for telegram_id={telegram_id}")
    return None


# def get_step1_buttons():
#     """
#     Generate buttons for step1_mobile_register_succesfully.
#     """
#     logger.info("Generating buttons for step1_mobile_register_succesfully.")
#     keyboard = [
#         [KeyboardButton(TRANSLATIONS["yes_show_objects"])],
#         [KeyboardButton("change_mobile get_step1_buttons")],
#         [KeyboardButton("contact_with_us")]
#     ]
#     logger.info(f"Step1 buttons: {keyboard}")
#     return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def validate_mobile_number(mobile_number: str) -> str:
    """
    Validate the format and API registration of a mobile number.

    Args:
        mobile_number (str): The mobile number provided by the user.

    Returns:
        str: Validation result:
             - "valid_and_registered_in_API"
             - "not_valid_format"
             - "valid_not_registered_in_API"
    """
    logger.info(f"Validating mobile number: {mobile_number}")

    # Check format
    if not (mobile_number.startswith("+374") and len(mobile_number) == 12) and \
       not (mobile_number.startswith("0") and len(mobile_number) == 9) and \
       not (mobile_number.startswith("374") and len(mobile_number) == 11):
        logger.warning(f"Mobile number does not match required format: {mobile_number}")
        return "not_valid_format"

    # Check API validation
    logger.info(f"Mobile number format valid. Checking registration via API: {mobile_number}")
    response = await validate_and_fetch_mobile_number(mobile_number)  # Assume this function interacts with the API
    if response:
        logger.info(f"Mobile number {mobile_number} is registered in the API.")
        return "valid_and_registered_in_API"
    else:
        logger.info(f"Mobile number {mobile_number} is not registered in the API.")
        return "valid_not_registered_in_API"


async def display_properties(validation_response, update):
    """
    Display details of each property in the validation response.
    INFO:database_operations:validation_response >>>>>>>>>  {'firstName': 'Մերի', 'lastName': 'Տեր-Հարությունովա', 'middleName': 'Դավթի',
     'phoneNumber': '37491995901', 'email': '', 'customerProperties': [{'apartment': '48 շենք', 'number': '1', 'code': 'A-48-1', 'type': 'Բնակարան'}]}

    INFO:api_helpers:Calling validation API with URL: https://condominium-server.technologist.ai/api/Customer/telegram/validation?phoneNumber=37494777513
INFO:handlers:Customer properties fetched: {'firstName': 'Արսեն', 'lastName': 'Նալբանդյան', 
'middleName': 'Գագիկի', 'phoneNumber': '37494777513', 'email': 'Arsen_nalbandyan@mail.ru',
 'customerProperties': [{'apartment': '48 շենք', 'number': '2', 'code': 'A-48-2', 'type': 'Բնակարան'},
  {'apartment': 'կայանատեղի 50/1', 'number': '2', 'code': 'P-501-2', 'type': 'Կայանատեղի'}, 

{'apartment': 'կայանատեղի 50/1', 'number': '7', 'code': 'P-501-7', 'type': 'Կայանատեղի'}]}


    """
    customer_properties = validation_response.get("customerProperties", [])
    if not customer_properties:
        await update.message.reply_text("No properties found.")
        return

    for prop in customer_properties:
        # Extract property details
        code = prop.get("code", "N/A")
        obj_type = prop.get("type", "N/A")
        apartment = prop.get("apartment", "N/A")
        number = prop.get("number", "N/A")

        # # Format the message
        # message = (
        #     f"Property Details:\n"
        #     f"Կոդ: {code}\n"
        #     f"Տեսակ: {obj_type}\n"
        #     f"{apartment}\n"
        #     f"N: {number}"
        # )
        # if obj_type== "Կայանատեղի":

            # Format the message
        message = (
            f"Property Details:\n"
            f"Code: {code}\n"
            f"Type: {obj_type}\n"
            f"Adress: {apartment}\n"
            f"N: {number}"
        )


        # Send the message
        await update.message.reply_text(message)


async def initialize(telegram_id):
    """
    Initialize user data and fetch user information from the database.

    Args:
        telegram_id (int): The Telegram ID of the user.

    Returns:
        dict: The user's data if found, or None if the user doesn't exist.
    """
    logger.info(f"Initializing data for telegram_id={telegram_id}")

    # If user_data doesn't exist, treat it as an expired session
    if telegram_id not in user_data:
        logger.warning(f"No session data found for telegram_id={telegram_id}. Treating as a new session.")

    # Check if the user exists in the database
    user = check_user_exists(telegram_id)
    logger.info(f"User data fetched from database: {user}")

    if user and user.get("mobile_number"):
        mobile_number = user["mobile_number"]
        logger.info(f"Fetching customer properties for mobile number: {mobile_number}")

        # Fetch customer properties
        validation_response = fetch_customer_properties(mobile_number)
        logger.info(f"Fetched properties: {validation_response}")

        # Reinitialize user_data for the user
        user_data[telegram_id] = {
            "state": "step1_mobile_register_succesfully",
            "prev_state": None,  # No previous state in a new session
            "mobile_number": mobile_number,
            "customer_properties": validation_response.get("customerProperties", []),
        }

        return user

    logger.warning(f"User with telegram_id={telegram_id} not found in database.")
    return None
