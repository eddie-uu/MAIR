"""
dictionary pricerange area food van Eddie

wij sturen dictionary =(query)

krijgen van Bence een lijst van dictionaries (zoals in .csv) met suggesties
(of lege lijst) het kan zijn dat sommige gegevens leeg zijn: dan none.
"""
import nltk
nltk.download('wordnet')
import pandas as pd
import re
from keyword_algorithm import keywordAlgorithm
from extract_info import extract_info
import decision_tree as dt
dtree = dt.createDecisionTree()
def Welcome():
    """
    Starts the dialog, and begins the state transitioning function.
    """
    print("Hello, welcome to our restaurant system. What kind of restaurant are you looking for? You can ask for restaurants by area, price range or food type.")
    firstmsg = input()
    first_msg_classification = dt.predict(firstmsg, dtree) #"inform"
    if first_msg_classification in ["inform", "hello", "thankyou"]:
        getUserPreferences(firstmsg)
    if first_msg_classification == "bye":
        Goodbye()


def getUserPreferences(message):
    """
    Finds out what type of restaurant the user is looking for.
    """
    query = keywordAlgorithm(message)
    if "pricerange" not in query.keys():
        query = {**query, **keywordAlgorithm(input("In what price range are you looking?"), mode="pricerange")}
    if "food" not in query.keys():
        query = {**query, **keywordAlgorithm(input("For what type of food are you looking?"), mode="food")}
    if "area" not in query.keys():
        query = {**query, **keywordAlgorithm(input("In what area are you looking?"), mode="area")}

    checkPreferences(query)

def checkPreferences(query):
    """
    Confirms the retrieved preferences with the user, and modifies them if needed.
    """
    print("You are looking for a restaurant", end="")
    if not query["pricerange"] == "dontcare":
        print(" in the " + query["pricerange"] + " pricerange", end="")
    if not query["food"] == "dontcare":
        print(" that serves " + query["food"], end="")
    if not query["area"] == "dontcare":
        print(" in the " + query["area"] + " of town", end="")
    print(". Is this correct? Type yes or no.")
    msg = input().lower()
    if dt.predict(msg, dtree) in ["negate", "deny"]:
        wrong = input("Which of the following is wrong? \n 1. Price range \n 2. Food type \n 3. Area")
        if wrong == "1":
            query = {**query, **keywordAlgorithm(input("In what price range are you looking?"), mode = "pricerange")}
        elif wrong == "2":
            query = {**query, **keywordAlgorithm(input("For what type of food are you looking?"), mode="food")}
        elif wrong == "3":
            query = {**query, **keywordAlgorithm(input("In what area are you looking?"), mode="area")}
        checkPreferences(query)
    elif dt.predict(msg, dtree) in ["affirm", "thankyou"]:
        getSuggestions(query)
    else:
        print("Sorry, I didn't understand that.")
        checkPreferences(query)

def getExtraPreferences(suggestions):
   
    satisfied = False
     
    while not satisfied:
        fmsg = input("would you like to add more preferences?")
        additional_pref = []
            
        if dt.predict(fmsg, dtree) in ["negate", "deny"]:
            satisfied = True
        elif dt.predict(fmsg, dtree) in ["affirm", "thankyou"]:
            smsg = input("What would you like to add? Choose one of the following options.\n 1. (not) busy \n 2. duration of your visit \n 3. child friendly \n 4. romantic \n 5. serves fast food \n 6. quality of the restaurant \n 7. suitable for a date \n 8. vegetarian options")
            if smsg == "1":
                choice = input("Do want a restaurant that is busy?").lower()
                if dt.predict(choice, dtree) in ["affirm", "thankyou"]:
                    additional_pref += ["busy"]
                elif dt.predict(choice, dtree) in ["negate", "deny"]:
                    additional_pref += ["not busy"]
                else: 
                    print("Sorry I did not get that. Please try again.")
            elif smsg == "2":
                choice = input("Would you like to spend a lot of time in the restaurant?").lower()
                if dt.predict(choice, dtree) in ["affirm", "thankyou"]:
                    additional_pref += ["not long time"]
                elif dt.predict(choice, dtree) in ["negate", "deny"]:
                    additional_pref += ["long time"]
                else:
                    print("Sorry I did not get that. Please try again.")
            elif smsg == "3":
                additional_pref += ["children"]
            elif smsg == "4":
                additional_pref += ["romantic"]
            elif smsg == "5":
                choice = input("Would you like a restaurant that serves fast food?").lower()
                if dt.predict(choice, dtree) in ["affirm", "thankyou"]:
                    additional_pref += ["fast food"]
                elif dt.predict(choice, dtree) in ["negate", "deny"]:
                    additional_pref += ["no fast food"]
                else:
                    print("Sorry I did not get that. Please try again.")
            elif smsg == "6":
                choice = input("Are you looking for a high quality restaurant?").lower()
                if dt.predict(choice, dtree) in ["affirm", "thankyou"]:
                    additional_pref += ["good restaurant"]
                elif dt.predict(choice, dtree) in ["negate", "deny"]:
                    additional_pref += ["bad restaurant"]  
                else:
                    print("Sorry I did not get that. Please try again.")
                    getExtraPreferences()
            elif smsg == "7":
                additional_pref += ["date"]
            elif smsg == "8":
                additional_pref += ["vegetarian"]
            elif dt.predict(smsg, dtree) in ["negate", "deny", "reqalts", "reqmore"]:
                    print("Unfortunately, you can only choose one of the additional preferences above.")
            else:
                print("Sorry I did not understand that. Please try again")
        else:
            print("Sorry I didn't understand that. Please try again.")
    
    ##TODO geef additional_pref door aan Bence 
    
    new_suggestions = functiebence(additional_pref) ##TODO fucntienaam aanpassen
    
    i = 0
    for restaurant in suggestions:
        if suggestions[i] in new_suggestions: #check if restaurant is still suitable after adding new preferences
            print(suggestions.iloc[i]['restaurantname'] + " meets all your preferences")
        else:
            print(suggestions.iloc[i]['restaurantname'] + " does not meet all your preferences")
        i += 1
        #apply all rules for which the properties of the restaurant satisfy the antecedent of the rule
        
        #contradictions


def getSuggestions(query):
    """
    Retrieves the suggestions from the database, given our user input.
    """
    suggestions = extract_info("restaurant_info.csv", query)
    i = 0
    satisfied = False
    while len(suggestions) > i and not satisfied:
        print(suggestions.iloc[i]['restaurantname'] + " is a nice place", end=" ")
        if not suggestions.iloc[[i]]["food"].empty: print("serving " + suggestions.iloc[i]["food"], end=" ")
        if not suggestions.iloc[[i]]["area"].empty: print("in the " + suggestions.iloc[i]["area"] + " of town", end=" ")
        if not suggestions.iloc[[i]]["pricerange"].empty: print(
            "in the " + suggestions.iloc[i]["pricerange"] + " pricerange", end="")
        print(".")
        choice = input(
            "Are you interested in this restaurant?")
        if dt.predict(choice, dtree) in ["affirm", "thankyou"]:
            satisfied = True
        elif dt.predict(choice, dtree) in ["negate", "deny", "reqalts", "reqmore"]:
            i += 1
            print("The following restaurant might be a good alternative.")
        else:
            print("Sorry, I didn't catch that. Please try again.")
    if not satisfied:
        print("Sadly we have no restaurants available that match your preferences. Try again. \n")
        Welcome()
        return

    giveInformation(suggestions, i)

def giveInformation(suggestions, suggestionIndex):
    """
    Asks whether the user needs extra information, and provides it where necessary.
    """
    satisfied = 0
    while not satisfied:
        more_info = input("Would you like some more information about the restaurant?")
        if dt.predict(more_info, dtree) in ["affirm", "thankyou"]:
            choice = input("What information would you like to have \n 1. Phone number \n 2. Address.")
            if choice == "1":
                if suggestions.iloc[[suggestionIndex]]["phone"].empty:
                    print("Sadly we have no phone number available for this restaurant.")
                else: print("The phone number is " + suggestions.iloc[suggestionIndex]["phone"] + ".")
            elif choice == "2":
                if suggestions.iloc[[suggestionIndex]]["addr"].empty or suggestions.iloc[[suggestionIndex]]["postcode"].empty:
                    print("Sadly we have no address available for this restaurant.")
                else:
                    print("The address is " + suggestions.iloc[suggestionIndex]["addr"] + " " +
                          suggestions.iloc[suggestionIndex]["postcode"] + ".")
        elif dt.predict(more_info, dtree) in ["negate", "deny"]:
            satisfied = True
        else:
            print("Sorry, I didn't catch that. Please try again.")
    Goodbye(suggestions.iloc[suggestionIndex]['restaurantname'])

def Goodbye(restaurantname = ""):
    """
    Ends the dialog.
    """
    if restaurantname != "":
        print("We hope you have a great meal at " + restaurantname + "!")
    else: print("Goodbye!")

Welcome()