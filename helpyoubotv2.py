#english version

import gspread  # импорти библиотеку
import telebot
from telebot import types # для указание типов
from workwithdb import *
from workwithdb import if_user_is_new
from Find_Dept_By_Code import Find_Dept_By_Code


import settings

# add_new_user_to_db(4544, "A-5")
# update_new_user_to_db(4544,"A-444-444" )

# print(Find_Dept_By_Code("P-5534-22"))

# print(Find_Dept_By_Code("P-5534-22091"))



token = '5559119243:AAH8F74c7N8qZ75R08QyrI7H8_DgcfCwSsU'
bot = telebot.TeleBot(token)
HELP = """
=============
'what address are you interested in 55 /xx , it should be one of 17, 20, 3, 33, 34 ?
->>>>>>>>>>>>>>>>>>
"""

gs = gspread.service_account(filename='credentials.json')  # подключаем файл с ключами и пр.
sh = gs.open_by_key('1w2wOpN5CCX5Xhlrqbm5e6eJWDXMchb-30j5EzvyxJBQ')  # подключаем таблицу по ID
wks = sh.get_worksheet(0)

# worksheet = sh.sheet1  # получаем первый лист
Avan_list_Adress = [17, 20, 3, 33, 34]
exist_count = 99 #some initial value
someParam = True
col_where_it_was_found = 0
# Cell_To_Find = "undefined In Hlyoubot"

##this function will return array with row where code was found
def Find_Code_By_address(kotorak, bnak_hamar, worksheet_sequence):
    wks = sh.get_worksheet(worksheet_sequence)
    global col_where_it_was_found
    # global Cell_To_Find
    settings.Cell_To_Find = "A-55" + str(kotorak) + "-" + str(bnak_hamar)
    print(settings.Cell_To_Find)
    cell_list = wks.find(settings.Cell_To_Find)  # find cell with given code number
    values_list = wks.row_values(cell_list.row)  # get whole row with "given code" that found what row is this
    col_where_it_was_found = cell_list.col

    print(cell_list.row)
    print(values_list)
    print(values_list[col_where_it_was_found])

    # find ամսավճար cell and get column , so when required duty will be calculated we will do (column_where_amsvachar_column_is -1)
    find_cell="ամսավճար"
    cell_amsavchar = wks.find(find_cell)
    # new_list = wks.row_values(cell_amsavchar.row)  # get whole row with "given code" that found what row is this
    column_where_amsvachar_column_is = cell_amsavchar.col

    print(f"{column_where_amsvachar_column_is} value of column_where_amsvachar_column_is " )

    final_duty_to_be_paid = values_list[column_where_amsvachar_column_is-2]

    settings.last_kotorak_value = kotorak
    settings.last_bnak_hamar = bnak_hamar
    settings.last_worksheet_sequence = worksheet_sequence


    print(final_duty_to_be_paid)




    return final_duty_to_be_paid

# Find_Code_By_address(20,10,0 )

# default values.

building_you_selected = "uknown"
# building_you_selected = "Avan4 55/17"





@bot.message_handler(commands=['start'])
def start(message):
    global current_user_id
    # global Cell_To_Find
    current_user_id = message.chat.id
    first_name_of_current_user = message.chat.first_name

    print (message.chat.first_name)
    print (message.chat.last_name)
    print (message.chat.id)


    if if_user_is_new(current_user_id):
        add_new_user_to_db(current_user_id, "New user to db called during start  ")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Avan4 55/17")
        btn2 = types.KeyboardButton("Avan4 55/20")
        btn_Avan6_1 = types.KeyboardButton("Avan6 55/3")
        btn_Avan6_2 = types.KeyboardButton("Avan6 55/33")
        btn_Avan6_3 = types.KeyboardButton("Avan6 55/34")
        btn_find_code_s_p = types.KeyboardButton("Find S or P by code")

        markup.add(btn1, btn2,btn_Avan6_1, btn_Avan6_2, btn_Avan6_3, btn_find_code_s_p)

        bot.send_message(message.chat.id, text="Hello, {0.first_name}! I will be helping you to get duty you have to pay , if any :) ".format(message.from_user), reply_markup=markup)


    else:
        print ("aaaaa Cell to find ixxxx")
        print (settings.Cell_To_Find)
        # update_new_user_to_db(current_user_id, "A-5517-253 ") #we don't need this row

        text_to_send_registered_user = "Hello, {}!\n  Looks like i rememeber you :) , are you looking for depths from  {} :) ? \n"


        text_to_send_registered_user = text_to_send_registered_user.format(first_name_of_current_user, settings.Cell_To_Find)

        # bot.send_message(message.chat.id, text = text_to_send_registered_user, reply_markup=markup)

        text_to_print = str(text_to_send_registered_user)  + " Choose which operation to do  -> go to home page, show depths for  " + str(settings.Cell_To_Find)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        correct_button = types.KeyboardButton("Yes, it's me")
        back = types.KeyboardButton("return to home menu")
        markup.add(correct_button, back)
        bot.send_message(message.chat.id, text=text_to_print, reply_markup=markup)


        # update_new_user_to_db(current_user_id, "A-5517-253 ") #we don't need this row


    # ====--------------------------
        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("Avan4 55/17")
        # btn2 = types.KeyboardButton("Avan4 55/20")
        # # btn3 = types.KeyboardButton("Avan4_Parking_Nkugh")
        # btn_Avan6_1 = types.KeyboardButton("Avan6 55/3")
        # btn_Avan6_2 = types.KeyboardButton("Avan6 55/33")
        # btn_Avan6_3 = types.KeyboardButton("Avan6 55/34")
        # # btn5 = types.KeyboardButton("Avan6_Parking_Nkugh")
        # # markup.add(btn1, btn2, btn3, btn4, btn5)
        # markup.add(btn1, btn2,btn_Avan6_1, btn_Avan6_2, btn_Avan6_3)
        # bot.send_message(message.chat.id, text="Hello, {0.first_name}! I will be helping you to get duty you have to pay , if any :) ".format(message.from_user), reply_markup=markup)
        # print (message.chat.first_name)
        # print (message.chat.last_name)
        # print (message.chat.id)


        # if if_user_is_new(current_user_id):
        #     add_new_user_to_db(current_user_id, "New user to db called during start  ")
        # else:
        #     update_new_user_to_db(current_user_id, "update_new_user_to_db is called during start ")


@bot.message_handler(content_types=['text'])
def func(message):
    global building_you_selected
    print(settings.selected_worksheet_is)
    global dutytopay
    # selected_worksheet_is = 0  #by default it will be 0



    dutytopay = 99999999 #some default value
    x = message.text

    if(message.text == "Avan4 55/17"):
        building_you_selected = "Avan4 55/17"
        settings.selected_worksheet_is = 0
        bot.send_message(message.chat.id, text="ok, 55/17 ->  i will need your flat number  please )")
        print("i will call fuction to get how much you should pay")
        print(building_you_selected)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("no need")
        back = types.KeyboardButton("return to home menu")
        markup.add( back)
        # bot.send_message(message.chat.id, text = " you may request another 'flat' within " + building_you_selected + "   or press button and go to home page ", reply_markup=markup)
    elif(message.text == "Avan4 55/20"):
        building_you_selected = "Avan4 55/20"
        settings.selected_worksheet_is = 0
        bot.send_message(message.chat.id, text="ok, Avan4 55/20 ->  i will need your flat number  please )")
        print("i will call fuction to get how much you should pay")
        print(building_you_selected)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("no need")
        back = types.KeyboardButton("return to home menu")
        markup.add( back)
        # bot.send_message(message.chat.id, text=" you may request another 'flat' within" + building_you_selected + "  or press button and go to home page ", reply_markup=markup)
    # ====Avan6 worksheet 2 -------------------------------------------------
    elif(message.text == "Avan6 55/33"):
        building_you_selected = "Avan6 55/33"
        settings.selected_worksheet_is = 2
        bot.send_message(message.chat.id, text="ok, " + building_you_selected + "->  i will need your flat number  please )")
        print("i will call fuction to get how much you should pay")
        print(building_you_selected)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("no need")
        back = types.KeyboardButton("return to home menu")
        markup.add( back)
        # bot.send_message(message.chat.id, text=" you may request another 'flat' within" + building_you_selected + "  or press button and go to home page ", reply_markup=markup)

    elif(message.text == "Avan6 55/3"):
        building_you_selected = "Avan6 55/3"
        settings.selected_worksheet_is = 2
        bot.send_message(message.chat.id, text="ok, " + building_you_selected + "->  i will need your flat number  please )")
        print("i will call fuction to get how much you should pay")
        print(building_you_selected)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("no need")
        back = types.KeyboardButton("return to home menu")
        markup.add( back)
        # bot.send_message(message.chat.id, text=" you may request another 'flat' within" + building_you_selected + "  or press button and go to home page ", reply_markup=markup)


    elif(message.text == "Avan6 55/34"):
        building_you_selected = "Avan6 55/34"
        settings.selected_worksheet_is = 2
        bot.send_message(message.chat.id, text="ok, " + building_you_selected + "->  i will need your flat number  please )")
        print("i will call fuction to get how much you should pay")
        print(building_you_selected)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("no need")
        back = types.KeyboardButton("return to home menu")
        markup.add( back)
        # bot.send_message(message.chat.id, text=" you may request another 'flat' within" + building_you_selected + "  or press button and go to home page ", reply_markup=markup)




    # ===
    elif(message.text == "Avan6"):
        building_you_selected = "Avan6"
        settings.selected_worksheet_is = 2
        bot.send_message(message.chat.id, text="ok, Avan6 ->  i will need your flat number  please )")
        print("i will call fuction to get how much you should pay avan 6")
        print(building_you_selected)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("no need")
        back = types.KeyboardButton("return to home menu")
        markup.add(back)

    elif(message.text == "Find S or P by code"):

        building_you_selected = "Avan4 55/17" # this to set some defsault value to initialize it -

        bot.send_message(message.chat.id, text="ok, ->  i will need Code number it shoild match  ~ format S-5534-107 or P-5534-26")
        print("i will call fuction to Find S or P by code")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)



        # btn1 = types.KeyboardButton("no need")
        back = types.KeyboardButton("return to home menu")
        markup.add(back)

    elif (x.startswith("S") or x.startswith("P")):
        temp_val = Find_Dept_By_Code(x)
        if temp_val == "myundefined":

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton("return to home menu")
            markup.add(back)
            bot.send_message(message.chat.id, text = (temp_val + " , there is no such 'Code'  , please try again with format: 'S-5534-107' or 'P-5534-26' ->>>----"), reply_markup=markup)

            print("не нашли")
        else:
            text_to_print = " Dear Customer , for Code in P or S  {} you are looking for   "
            temp_text = text_to_print.format(x)
            if temp_val.startswith("-"): #" means we with minus at the beginning,
                    bot.send_message(message.chat.id, text = (temp_text + ", you should pay ->>>"))
                    bot.send_message(message.chat.id, text = temp_val)
            else:
                    bot.send_message(message.chat.id, text = (temp_text + "You don't have much to pay, your balance is positive"))
                    bot.send_message(message.chat.id, text = temp_val)


            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton("return to home menu")
            markup.add(back)
            bot.send_message(message.chat.id, text = " you may request another 'Code';  it shoild match  ~ format S-5534-107 or P-5534-26  or press button and go to home page ", reply_markup=markup)


    # print(type(x))
    elif (x.isnumeric()==True):
        print("numeric")

        if int(x) < 281 and (int(x) >= 1):# and building_you_selected : to be ADDDDDDDDDDDDDDDDDDEDDDDDDDDDDDDDDDDDDDDDDDDDDD
            # "Avan4 55/20" --- Avan6 55/3 ---Avan6 55/33 Avan6 55/34
            x = int(x)
            if settings.selected_worksheet_is == 0:
                get_kototak_from_selection = building_you_selected[9:11]
                if (int(get_kototak_from_selection) == 17 or int(get_kototak_from_selection) == 20):
                    dutytopay = Find_Code_By_address(get_kototak_from_selection, x, settings.selected_worksheet_is )
                    # ins_data_to_db(get_kototak_from_selection , flat_number, config.selected_worksheet_is ,     -- this supposed to be flat_number
                    #  e.g. Cell_To_Find  A-5517-34
                    update_new_user_to_db(current_user_id, settings.Cell_To_Find)
                    print(" update db row with update_new_user_to_db(current_user_id, Cell_To_Find) ")
                    print(current_user_id)
                    print(settings.Cell_To_Find)


                elif int(get_kototak_from_selection) ==20:
                   if x==187 or x==188:
                       print("plz correct that row for 20 flat 187/188")
                       markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                       # btn1 = types.KeyboardButton("no need")
                       back = types.KeyboardButton("return to home menu")
                       markup.add(back)
                       bot.send_message(message.chat.id, text = " you may request another 'flat' within {" + building_you_selected + "}  or press button and go to home page ", reply_markup=markup)

                   else:
                        dutytopay = Find_Code_By_address(get_kototak_from_selection, x, settings.selected_worksheet_is )

                else:
                   print ("get_kototak_from_selection suppose to be 17 or 20 for worksheet 0, error - > ")

            elif settings.selected_worksheet_is== 2 and len(building_you_selected)==11 and x < 71:   # "Avan4 55/20" --- Avan6 55/3 ---Avan6 55/33 Avan6 55/34
                get_kototak_from_selection = building_you_selected[9:11]
                if (int(get_kototak_from_selection) == 33):# --------------> building selection was 33
                    dutytopay = Find_Code_By_address(get_kototak_from_selection, x, settings.selected_worksheet_is )
                    update_new_user_to_db(current_user_id, settings.Cell_To_Find)

                elif int(get_kototak_from_selection) ==34:# --------------> building selection was 34
                   dutytopay = Find_Code_By_address(get_kototak_from_selection, x, settings.selected_worksheet_is )
                   update_new_user_to_db(current_user_id, settings.Cell_To_Find)

            elif settings.selected_worksheet_is == 2 and len(building_you_selected)==10 and x < 71:   # "Avan4 55/20" --- Avan6 55/3 ---Avan6 55/33 Avan6 55/34
                get_kototak_from_selection = building_you_selected[9:10]
                if (int(get_kototak_from_selection) == 3):  #building selection was 3
                    dutytopay = Find_Code_By_address(get_kototak_from_selection, x, settings.selected_worksheet_is )
                    update_new_user_to_db(current_user_id, settings.Cell_To_Find)


            else:
                # this means dutytopay = 99999999 means it was not yet intialiized , so we need to skip block below.
                print ("flat is not in range , error - > need to debug maybe? ")
                print (building_you_selected)
                text_to_print = " entered flat is not in range, please select proper one "

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton("return to home menu")
                markup.add(back)
                bot.send_message(message.chat.id, text=text_to_print, reply_markup=markup)

            print("type(dutytopay) ------------ " )
            print(type(dutytopay))

            dutytopay = str(dutytopay)

            if dutytopay != "99999999":
                print ("flat is good")
                print (building_you_selected)
                # bot.send_message(message.chat.id, text="for this flat you must pay .")
                text_to_print = " Dear Customer , for building {} and flat number {}  "
                temp_text ="uknownnnn"
                temp_text = text_to_print.format(building_you_selected,int(x))

                print("type(dutytopay) ------------ " )
                print(type(dutytopay))
                if dutytopay.startswith("-"): #" means we with minus at the beginning,
                    bot.send_message(message.chat.id, text = (temp_text + ", you should pay ->>>"))
                    bot.send_message(message.chat.id, text = dutytopay)
                else:
                    bot.send_message(message.chat.id, text = (temp_text + "You don't have much to pay, your balance is positive"))
                    bot.send_message(message.chat.id, text = dutytopay)


                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                back = types.KeyboardButton("return to home menu")
                markup.add(back)
                bot.send_message(message.chat.id, text = " you may request another 'flat' within {" + building_you_selected + "}  or press button and go to home page ", reply_markup=markup)



            else:
                print("dutytopay = 99999999 means it was not yet intialiized ")



        else:
            print ("flat is not good ")
            print (building_you_selected)
            text_to_print = " entered flat is not in range, please select proper one "
            # temp_text = text_to_print.format(building_you_selected,int(x))
            # bot.send_message(message.chat.id, text = text_to_print)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton("return to home menu")
            markup.add(back)
            bot.send_message(message.chat.id, text=text_to_print, reply_markup=markup)



    elif (message.text == "Yes, it's me"):
        # bot.send_message(message.chat.id, "У меня нет имени..")
        # 'A-5517-10
        # settings.Cell_To_Find = "A-5517-10"
        get_kotorak = settings.Cell_To_Find[4:6] # for case with 'A-5517-10 - > 17
        get_kotorak = int(get_kotorak)
        leng = len(settings.Cell_To_Find)
        get_bnak_hamar = settings.Cell_To_Find[7:leng] # for case with 'A-5517-10 - > 10
        get_bnak_hamar = int(get_bnak_hamar)

        if get_kotorak ==17 or get_kotorak ==20:
            worksheet_sequence = 0
        elif get_kotorak == 3 or get_kotorak == 33 or get_kotorak == 34:
            worksheet_sequence = 2

        else:
            print ("other worksheets not yet coded.")

        print(" Find_Code_By_address(get_kotorak, get_bnak_hamar, worksheet_sequence): ")
        print(get_kotorak)
        print(get_bnak_hamar)
        print(worksheet_sequence)
        dept_for_this_user_in_google_doc = 0  #wwwwwhhhhhhhhhhhhhtFFFFFFFFFFFFFF?
        dept_for_this_user_in_google_doc = Find_Code_By_address(get_kotorak, get_bnak_hamar, worksheet_sequence)


        dept_for_this_user_in_google_doc = str(dept_for_this_user_in_google_doc)

        if dept_for_this_user_in_google_doc != "99999999":
            print("flat is good")

            building_you_selected = str(get_kotorak)
            print(building_you_selected)
            # bot.send_message(message.chat.id, text="for this flat you must pay .")
            text_to_print = " Dear Customer , for building {} and flat number {}  "
            temp_text = "uknownnnn"
            temp_text = text_to_print.format(building_you_selected, int(get_bnak_hamar))

            print("type(dept_for_this_user_in_google_doc) ------------ ")
            print(type(dept_for_this_user_in_google_doc))
            if dept_for_this_user_in_google_doc.startswith("-"):  # " means we with minus at the beginning,
                bot.send_message(message.chat.id, text=(temp_text + ", you should pay ->>>"))
                bot.send_message(message.chat.id, text=dept_for_this_user_in_google_doc)
            else:
                bot.send_message(message.chat.id,
                                 text=(temp_text + "You don't have much to pay, your balance is positive"))
                bot.send_message(message.chat.id, text=dept_for_this_user_in_google_doc)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            back = types.KeyboardButton("return to home menu")
            markup.add(back)
            bot.send_message(message.chat.id, text=" you may request another 'flat' within {" + building_you_selected + "}  or press button and go to home page ", reply_markup=markup)
        else:
            print("dutytopay = 99999999 means it was not yet intialiized ")



    elif(message.text == "Как меня зовут?"):
        bot.send_message(message.chat.id, "У меня нет имени..")

    elif message.text == "Что я могу?":
        bot.send_message(message.chat.id, text="Поздороваться с читателями")

    elif (message.text == "return to home menu"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        btn1 = types.KeyboardButton("Avan4 55/17")
        btn2 = types.KeyboardButton("Avan4 55/20")
        btn_Avan6_1 = types.KeyboardButton("Avan6 55/3")
        btn_Avan6_2 = types.KeyboardButton("Avan6 55/33")
        btn_Avan6_3 = types.KeyboardButton("Avan6 55/34")
        btn_find_code_s_p = types.KeyboardButton("Find S or P by code")
        # markup.add(btn1, btn2, btn3, btn4, btn5)
        markup.add(btn1, btn2,btn_Avan6_1, btn_Avan6_2, btn_Avan6_3, btn_find_code_s_p)
        bot.send_message(message.chat.id, text="Hello, {0.first_name}! I will be helping you to get duty you have to pay , if any :) ".format(message.from_user), reply_markup=markup)

        # bot.send_message(message.chat.id, text="Hello, {0.first_name}! I will be helping you to get duty you have to pay , if any :) ".format(message.from_user), reply_markup=markup)
        bot.send_message(message.chat.id, text="We are in home page now ! ", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back = types.KeyboardButton("return to home menu")
        markup.add(back)
        bot.send_message(message.chat.id, text="Sorry , i don't know what do you mean, you suppose to enter flat number within 1-301 range, please try again :  ",  reply_markup=markup)

bot.polling(none_stop=True)






















# gs = gspread.service_account(filename='credentials.json')  # подключаем файл с ключами и пр.
# sh = gs.open_by_key('1w2wOpN5CCX5Xhlrqbm5e6eJWDXMchb-30j5EzvyxJBQ')  # подключаем таблицу по ID
# # worksheet = sh.sheet1  # получаем первый лист

# Avan_list_Adress = [17, 20, 3, 33, 34]
# exist_count = 99 #some initial value

# #we will ask to enter proper values till user realize that there is no other way
# def func_if_entered_data_is_correct(validate_adress):
#     global exist_count
#     x = True
#     if validate_adress in Avan_list_Adress:
#         exist_count = Avan_list_Adress.index(validate_adress)
#         print(exist_count)
#     else:
#         x = False
#         print("please enter proper values")
#     return x

# def func_if_entered_data_is_correct2(flat_number):
#     x = True
#     if flat_number < 281:
#       x = True
#     else:
#         x = False
#         print("please enter proper values")
#     return x


# # print(func_if_entered_data_is_correct(25))
# # print(func_if_entered_data_is_correct(122))
# # print(func_if_entered_data_is_correct2(400))
# # print(func_if_entered_data_is_correct2(0))

# col_where_it_was_found = 0

# ##this function will return array with row where code was found
# def Find_Code_By_address(kotorak, bnak_hamar):
#     global col_where_it_was_found
#     Cell_To_Find = "A-55" + str(kotorak) + "-" + str(bnak_hamar)
#     print(Cell_To_Find)
#     cell_list = wks.find(Cell_To_Find)  # find cell with given code number
#     values_list = wks.row_values(cell_list.row)  # get whole row with "given code" that found what row is this
#     col_where_it_was_found = cell_list.col
#     print(cell_list.row)
#     print(values_list)
#     return values_list

# # ----------

# # cell_list = wks.find("A-5520-27")
# # print("Found something at Row % s Column % s" % (cell_list.row, cell_list.col))

# # enter data ->
# print('what address are you interested in 55 /xx , it should be one of 17, 20, 3, 33, 34 ?')
# AddressToFind = int(input())
# func_if_entered_data_is_correct(AddressToFind) # validate inside fucntion if data is ok
# print('what flat  are you interested in 55 / ' + str(AddressToFind) + ' ? ')
# FlatToFind = int(input())
# func_if_entered_data_is_correct2(FlatToFind) # validate inside fucntion if data is ok
# #assuming data is good: exist_count = Avan_list_Adress.index(validate_adress) is showing proper worksheet

# print(exist_count)
# wks = sh.get_worksheet(exist_count)
# x = []
# x = Find_Code_By_address(AddressToFind, FlatToFind)



# print(col_where_it_was_found)
# print ("You have to pay my friend: ")
# print(x[col_where_it_was_found])



# if AddressToFind in Avan_list_Adress:
#     exist_count = Avan_list_Adress.index(AddressToFind)
#     print ("ok")
# else:
#     print("no such address, it should be one of -> 17, 20, 3, 33, 34 ")
#
# if FlatToFind < 281:
#     print ("ok - flat should be less than 280")
# else:
#     print("no such flat exist , it should be between 1 and 280 ")

# element exists in list
# exist_count = Avan_list_Adress.index(AddressToFind)
# print(str(exist_count)+"exist_count")

# # checking if it is more than 0
# if exist_count >= 0:
#     print("Yes,  exists in list")
# else:
#     print("No,  does not exists in list")


#get_code_of adress to validate




#
#
# # worksheet2 = sh.worksheet(self, "Avan 4 ParkingNkugh")
# # sh.worksheet()
#
# res = wks.get_all_records()  # считываем все записи (массив: ключ-значение)
# # res = worksheet.get_all_values()  # считываем все значения
# res2 = worksheet.row_values(1)  # получаем первую строчку таблицы
# res3 = worksheet.col_values(1)  # получаем первую колонку таблицы
# res4 = worksheet.get('A2')  # получаем заданную ячейку
# res5 = worksheet.get('A2:C2')  # получаем заданный диапазон
#
# print(res)  # выводим в консоль
#
# print(res2)  # выводим в консоль
#
# print(res3)  # выводим в консоль
#
# print(res4)  # выводим в консоль
#
# print(res5)  # выводим в консоль
#
#
#

