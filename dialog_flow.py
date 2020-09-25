"""
dictionary pricerange area food van Eddie

wij sturen dictionary =(query)

krijgen van Bence een lijst van dictionaries (zoals in .csv) met suggesties
(of lege lijst) het kan zijn dat sommige gegevens leeg zijn: dan none.
"""
from __future__ import print_function
from keyword_algorithm import keywordAlgorithm
from extract_info import extract_info
from extract import extract_settings, change_setting
import nltk
import time
import pandas as pd
import re
import json
import decision_tree as dt
nltk.download('wordnet')
dtree = dt.createDecisionTree()
configurations = extract_settings()

try:
    import __builtin__
except ImportError:
    # Python 3
    import builtins as __builtin__

def input(prompt = ''):
    if configurations['RESPONSE_DELAY']['value'].lower() == 'true':
        time.sleep(1)

    return __builtin__.input(prompt)

def print(*args, **kwargs):
    if configurations['RESPONSE_DELAY']['value'].lower() == 'true':
        time.sleep(1)

    for arg in args:
        if isinstance(arg, str) and configurations['OUTPUT_IN_CAPS']['value'].lower() == 'true':
            return __builtin__.print(arg.upper())
    return __builtin__.print(*args, **kwargs)

def Welcome():
    """
    Starts the dialog, and begins the state transitioning function.
    """
    print("Hello, welcome to our restaurant system. What kind of restaurant are you looking for? You can ask for restaurants by area, price range or food type.")
    firstmsg = input()
    if (firstmsg == 'settings'):
        configurateSettings()
    else:
        first_msg_classification = dt.predict(firstmsg, dtree) #"inform"
        if first_msg_classification in ["inform", "hello", "thankyou"]:
            getUserPreferences(firstmsg)
        elif first_msg_classification == "bye":
            Goodbye()

def configurateSettings():
    settings = extract_settings()
    responseDelay = configurations['RESPONSE_DELAY']['value']
    configurations['RESPONSE_DELAY']['value'] = 'false'

    finishedSettings = False
    while not finishedSettings:
        print("Which setting would you like to change?")
        counter = 1
        settingsIndex = {}

        for setting in settings:
            print(str(counter) + ". " + settings[setting]["text"])
            settingsIndex[str(counter)] = {"key": setting, "value": settings[setting]} 
            counter += 1
        
        saveAndRestart = counter
        cancel = counter + 1
        print(str(saveAndRestart) + ". Save and close")
        print(str(cancel) + ". Cancel")

        choice = input("> ")

        if (choice == str(saveAndRestart)):
            finishedSettings = True
            change_setting(settings)
            print("Configurations have been saved, closing application now...")
        elif (choice == str(cancel)):
            finishedSettings = True
            print("Configurations will remain the same, closing application now...")
        elif choice in settingsIndex:
            settingKey = settingsIndex[choice]["key"]
            settingValues = settingsIndex[choice]["value"]

            validChoices = {"int": "^\d+$", "bool": 'true|false|True|False|TRUE|FALSE'}
            print("Current setting for " + str(settingKey) + " is: " + str(settingValues["value"]))
            print("To which value would you like to change this? (Value must be of the type: " + str(settingValues["valueType"]) + " )")

            if (settingValues["valueType"] == "ENUM"):
                enumOptions = ""
                for option in settingValues["valueOptions"]:
                    print("- " + str(option["value"]))
                    enumOptions += str(option["value"]).lower() + "|"
                validChoices["ENUM"] = enumOptions[:-1] if len(enumOptions) > 0 else enumOptions

            choice = input("> ")

            pattern = re.compile(validChoices[str(settingValues["valueType"])])
            if pattern.match(choice) != None:
                print("Settings for " + settingKey + " have been changed from " + str(settingValues["value"]) + " to " + choice)
                settings[settingKey]["value"] = choice
            else:
                print("Sorry, the given input is invalid")
            time.sleep(1)
        else:
            print("Sorry, the given input could not be recognized")
            time.sleep(1)

    configurations['RESPONSE_DELAY']['value'] = responseDelay

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



def getSuggestions(query):
    """
    Retrieves the suggestions from the database, given our user input.
    """
    suggestions = extract_info("data/restaurant_info.csv", query)
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