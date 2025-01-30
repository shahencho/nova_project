TRANSLATIONS = {
    # Welcome message shown when the user first enters the bot
    "welcome_message": (
        "Ողջույն, {name}: Ես Իննովա Մենեջմենթի բոտն եմ և կօգնեմ Ձեզ տեղեկություն ստանալ "
        "Ձեր սեփականության ընթացիկ պարտքի կամ կանխավճարի մասին և այլ օգտակար ինֆորմացիա համատիրության աշխատանքների մասին։"
    ),
    # Prompt for entering mobile number in a valid format
    "ask_mobile_number": (
        "Խնդրում ենք մուտքագրեք ձեր հեռախոսահամարը, որը գրանված է համատիրության գրանցամատյանում այս ֆորմատով՝ "
        "+374xxxxxxxx կամ 0xxxxxxxx to test use - < 37491995901 > <37494777513> < 37455024479> <37494555585> "
    ),
    # Message when displaying found objects assigned to the user
    # "We found objects assigned to you. Select one to view details:"
    "found_objects": "Այս համարին  կցված են հետևյալ օբյեկտները։ Ընտրեք մեկը՝ մանրամասներ դիտելու համար։\n\r",
    # Button text for changing associated mobile number
    # "Change Associated Mobile"
    "change_mobile": "Փոխել կցված հեռախոսահամարը",
    # Error message when failing to fetch property details
    # "Failed to fetch property details. Please try again later."
    "fetch_details_failed": "Չհաջողվեց ստանալ գույքի մանրամասները։ Խնդրում ենք փորձել ավելի ուշ։",
    # Header for payment history
    # "Payment History for {code}:\n{history}"
    "payment_history": "Վճարումների պատմություն {code}-ի համար:\n{history}",
    # Message when no transactions are found for an object
    # "Payment History for {code}: No transactions found."
    "no_transactions": "{code}-ի համար վճարումներ չեն գտնվել։",
    # Question asking the user if they want to see payment details
    # "Do you want to see payment details for this object?"
    "ask_to_view_details": "Ցանկանու՞մ եք տեսնել այս օբյեկտի վճարումների մանրամասները։",
    # Prompt to enter a new mobile number
    # "Please enter your new phone number in the format +374xxxxxxxx or 0xxxxxxxx."
    "enter_new_mobile": "Խնդրում ենք մուտքագրել Ձեր նոր հեռախոսահամարը հետևյալ ֆորմատով՝ +374xxxxxxxx կամ 0xxxxxxxx։ to test use - < 37491995901 > <37494777513> < 37455024479> <37494555585> ",
    # Message confirming the found mobile number and associated properties
    "mobile_saved_in_db_found": " \n\nԳտանք Ձեր հեռախոսահամարին կցված գույքը։ (Վերջին անգամ օգտագործված հեռախոսահամարով) ",
    # Prompt to choose a flat building
    "choose_flat_building": (
        "Դուք ընտրել եք ԲՆԱԿԱՐԱՆ, ընտրեք շենքը "
        "(ճշգրիտ հասցեն կարող եք ճշտել սեփականության վկայականից)"
    ),
    # Prompt to enter a flat number
    "enter_flat_number": (
        "Դուք ընտրեցիք {building} շենքը։ Ընտրեք բնակարանը կամ միավորի համարը "
        "(ճշգրիտ հասցեն կարող եք ճշտել սեփականության վկայականից)"
    ),
    # Prompt to choose a public space building
    "choose_public_space_building": (
        "Դուք ընտրել եք \"Հասարակական Տարածք\", ընտրեք շենքը "
        "(ճշգրիտ հասցեն կարող եք ճշտել սեփականության վկայականից)"
    ),
    # Prompt to enter a public space ID
    "enter_public_space_id": (
        "Դուք ընտրեցիք {building} շենքը։ Ընտրեք միավորի համարը "
        "(ճշգրիտ հասցեն կարող եք ճշտել սեփականության վկայականից)"
    ),
    # Prompt to choose a parking building
    "choose_parking_building": (
        "Դուք ընտրել եք \"Կայանատեղի\", ընտրեք շենքը "
        "(ճշգրիտ հասցեն կարող եք ճշտել սեփականության վկայականից)"
    ),
    # Prompt to enter a parking ID
    "enter_parking_id": (
        "Դուք ընտրեցիք {building} շենքը։ Ընտրեք կայանատեղի համարը "
        "(ճշգրիտ հասցեն կարող եք ճշտել սեփականության վկայականից)"
    ),
    # Mobile response header when properties are found
    "mobile_response_header": "Գտանք մի քանի գույք կցած այս համարին՝",
    # Mobile response for each object
    "mobile_response_object": "{index}. {code} ({type})։ Պարտքը կազմում է {debt} դրամ",

    "found_properties": "Գտնվել են հետևյալ գույքերը՝ {properties}",

    # "case_no_debt_no_deposit": "{code} DEBT is 0, and deposit is 0, meaning all payments are up to date. Thanks for your timely payments!", 
    # "case_debt_no_deposit": "{code} You have debt, amount debt is: {debt}. Please do payments ASAP.",
    # "case_no_debt_with_deposit": "{code} You have deposit, deposit amount = {deposit}. Thanks for closing payment on time.",
    # "case_debt_and_deposit": "{code} You have deposit amount = {deposit}. You have debt amount = {debt}."

    "case_no_debt_no_deposit": "{code}  ՊԱՐՏՔԸ հավասար է 0-ի, կանխավճարն էլ հավասար է 0-ի, ինչը նշանակում է, որ բոլոր վճարումները ժամանակին են։ Շնորհակալություն Ձեր պարտաճանաչության համար։", 
    # "case_debt_no_deposit": "{code}  Դուք ունեք պարտք, պարտքի գումարը՝  {debt}. ։ Խնդրում ենք հնարավորինս շուտ կատարել վճարումը։",
    "case_no_debt_with_deposit": "{code} Դուք ունեք կանխավճար, գումարը՝  = {deposit}. ։ Շնորհակալություն ժամանակին վճարումները կատարելու համար։",
    "case_debt_and_deposit": "{code} Դուք ունեք կանխավճար՝ {deposit}, և պարտք՝ {debt}։",

    "mobile_number_saved": "Ձեր նոր հեռախոսահամարը {new_mobile_number} պահպանվել է։",

    "yes_show_objects": "Այո, ցույց տալ իմ օբյեկտները",

    "back_to_objects": "Վերադառնալ",

    "no_mobile_number_linked": "no_mobile_number_linked",

    "Refresh": "Թարմացնել",

    "Back1": "Վերադառնալ",

    "Blady": "Վերադառնալ> ",  
    
    "choose_action": "choose_action",
  

    "invalid_mobile_format": "invalid_mobile_format", 

    "back_to_main_menu": "back_to_main_menu",

    "case_debt_no_deposit":  (
    "Դուք ունեք պարտք, պարտքի գումարը՝  {debt}. ։ Խնդրում ենք հնարավորինս շուտ կատարել վճարումը։\n "
    "Վճարում կարող եք իրականացնել ինչպես բանկային փոխանցումով, այնպես էլ idram, Easy Wallet, Tel Cell, Fast Shift հավելվածներով և Tel Cell, EasyPay, FastShift տերմինալներով։\n"
    "Բանկային փոխանցման համար՝\n"
    "Հաշվեհամար՝ 1660030213905000\n"
    "Բանկ՝ էվոկաբանկ\n"
    "Ստացող՝ «Վերածնունդ թաղամաս համատիրություն»\n"
    "Վճարում կատարելիս նպատակը դաշտում նշել տվյալ գույքի վճարման կոդը: Օրինակ՝ «A-5520-6» կամ «P-5520-2» կամ «S-5520-212»։\n"
    "\nԱյս գույքի վճարման կոդն է՝ {code}"
)

}
