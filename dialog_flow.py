import nltk
import time
#nltk.download('wordnet')
import pandas as pd
import re
import json
import random
from keyword_algorithm import keywordAlgorithm
from extract_info import extract_info
from extract import extract_settings, change_setting
import decision_tree as dt
dtree = dt.createDecisionTree()

def Welcome():
    """
    Starts the dialog, and begins the state transitioning function.
    """
    print("Hello, welcome to our restaurant system. What kind of restaurant are you looking for? You can ask for restaurants by area, price range or food type.")
    firstmsg = input()
    if (firstmsg == "settings"):
        configurateSettings()
    else:

        first_msg_classification = dt.predict(firstmsg, dtree)  # "inform"
        if first_msg_classification in ["inform", "hello", "thankyou"]:
            query = keywordAlgorithm(firstmsg)
            checkQuery(query)
        if first_msg_classification == "bye":
            Goodbye()


def checkQuery(query):
    solutions = extract_info("restaurant_info.csv", query)
    print(len(solutions))
    print(query)
    if len(solutions) == 0:
        alternativeSuggestions(query)
    if len(solutions) == 1 or len(query) == 3:
        if "pricerange" not in query:
            query["pricerange"] = "dontcare"
        if "food" not in query:
            query["food"] = "dontcare"
        if "area" not in query:
            query["area"] = "dontcare"
        if len(solutions) == 1: print("There is only one restaurant available that satisfies your preferences:")
        getSuggestions(query)
    if len(solutions) > 1:
        getUserPreferences(query)

def alternativeSuggestions(oldquery):
    print("There are no suggestions that satisfy your preferences. The following alternatives are available:")
    alternatives = []
    newquery = oldquery
    #PRICERANGE SUBSTITUTIONS
    if query["pricerange"] == "cheap":
        newquery["pricerange"] = "moderate"
        alternatives.append(extract_info("restaurant_info.csv", newquery))
    elif query["pricerange"] == "moderate":
        newquery["pricerange"] = "expensive"
        alternatives.append(extract_info("restaurant_info.csv", newquery))
    newquery = oldquery
    #AREA SUBSTITUTIONS
    if oldquery["area"] in ["centre", "north", "west"]:
        for area in ["centre", "north", "west"]:
            newquery["area"] = area
            alternatives.append(extract_info("restaurant_info.csv", newquery))
    if oldquery["area"] in ["centre", "north", "east"]:
        for area in ["centre", "north", "east"]:
            newquery["area"] = area
            alternatives.append(extract_info("restaurant_info.csv", newquery))
    if oldquery["area"] in ["centre", "south", "west"]:
        for area in ["centre", "south", "west"]:
            newquery["area"] = area
            alternatives.append(extract_info("restaurant_info.csv", newquery))
    if oldquery["area"] in ["centre", "south", "east"]:
        for area in ["centre", "south", "east"]:
            newquery["area"] = area
            alternatives.append(extract_info("restaurant_info.csv", newquery))

    #FOODTYPE SUBSTITUTIONS
    newquery = oldquery
    if oldquery["food"] in ["thai", "chinese", "korean", "vietnamese", "asian oriental"]:
        for food in ["thai", "chinese", "korean", "vietnamese", "asian oriental"]:
            newquery["food"] = food
            alternatives.append(extract_info("restaurant_info.csv", newquery))
    if oldquery["food"] in ["mediterranean", "spanish", "portuguese", "italian", "romanian", "tuscan", "catalan"]:
        for food in ["mediterranean", "spanish", "portuguese", "italian", "romanian", "tuscan", "catalan"]:
            newquery["food"] = food
            alternatives.append(extract_info("restaurant_info.csv", newquery))
    if oldquery["food"] in ["french", "european", "bistro", "swiss", "gastropub", "traditional"]:
        for food in ["french", "european", "bistro", "swiss", "gastropub", "traditional"]:
            newquery["food"] = food
            alternatives.append(extract_info("restaurant_info.csv", newquery))
    if oldquery["food"] in ["north american", "steakhouse", "british"]:
        for food in ["north american", "steakhouse", "british"]:
            newquery["food"] = food
            alternatives.append(extract_info("restaurant_info.csv", newquery))
    if oldquery["food"] in ["lebanese", "turkish", "persian"]:
        for food in ["lebanese", "turkish", "persian"]:
            newquery["food"] = food
            alternatives.append(extract_info("restaurant_info.csv", newquery))
    if oldquery["food"] in ["international", "modern european", "fusion"]:
        for food in ["international", "modern european", "fusion"]:
            newquery["food"] = food
            alternatives.append(extract_info("restaurant_info.csv", newquery))
    random.shuffle(alternatives)
    for i in range(0, 3):
        print(i + ": ", end="")
        print(alternatives.iloc[i]['restaurantname'] + " is a nice place", end=" ")
        if not alternatives.iloc[[i]]["food"].empty: print("serving " + alternatives.iloc[i]["food"], end=" ")
        if not alternatives.iloc[[i]]["area"].empty: print("in the " + alternatives.iloc[i]["area"] + " of town", end=" ")
        if not alternatives.iloc[[i]]["pricerange"].empty: print(
            "in the " + alternatives.iloc[i]["pricerange"] + " pricerange", end="")
        print(".")
    print("Do you want to:")
    print("1. Change your preferences")
    print("2. Choose one of these alternatives")
    input = input()
    if input == 1:
        restatePreferences(oldquery)
    if input == 2:
        suggindex = input("Which suggestion would you like?")
        giveInformation(suggestions, suggindex)

def restatePreferences(query):
    wrong = input("Which of the following would you like to change? \n 1. Price range \n 2. Food type \n 3. Area")
    if wrong == "1":
        query = {**query, **keywordAlgorithm(input("In what price range are you looking?"), mode="pricerange")}
    elif wrong == "2":
        query = {**query, **keywordAlgorithm(input("For what type of food are you looking?"), mode="food")}
    elif wrong == "3":
        query = {**query, **keywordAlgorithm(input("In what area are you looking?"), mode="area")}
    getSuggestions(query)

def configurateSettings():
    settings = extract_settings()
    
    # print(json.dumps(settings, indent=4))
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

            validChoices = {"int": "^\d+$", "bool": 'true|false'}
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

def getUserPreferences(query):
    """
    Finds out what type of restaurant the user is looking for.
    """
    if "pricerange" not in query.keys():
        query = {**query, **keywordAlgorithm(input("In what price range are you looking?"), mode="pricerange")}
        checkQuery(query)
        return
    if "food" not in query.keys():
        query = {**query, **keywordAlgorithm(input("For what type of food are you looking?"), mode="food")}
        checkQuery(query)
        return
    if "area" not in query.keys():
        query = {**query, **keywordAlgorithm(input("In what area are you looking?"), mode="area")}
        checkQuery(query)
        return

    #checkPreferences(query)

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
            print("Looking for alternatives...")
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
                    print("The address is " + str(suggestions.iloc[suggestionIndex]["addr"]) + " " +
                          str(suggestions.iloc[suggestionIndex]["postcode"]) + ".")
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