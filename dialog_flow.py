from __future__ import print_function
from keyword_algorithm import KeywordAlgorithm
from decision_tree import DecisionTree
from mlp import mlp_test, mlp
from extract_info import ExtractInfo
from extract import Extract
import nltk
import time
import pandas as pd
import re
import json
import random
from imply import implications
import pickle
import os

nltk.download('wordnet')

try:
    import __builtin__
except ImportError:
    # Python 3
    import builtins as __builtin__

extract = Extract()
extractConfig = extract.extract_settings()

def input(prompt = ''):
    if extractConfig['RESPONSE_DELAY']['value'].lower() == 'true':
        time.sleep(1)

    return __builtin__.input(prompt)

def print(*args, **kwargs):
    if extractConfig['RESPONSE_DELAY']['value'].lower() == 'true':
        time.sleep(1)

    for arg in args:
        if isinstance(arg, str) and extractConfig['OUTPUT_IN_CAPS']['value'].lower() == 'true':
            return __builtin__.print(arg.upper())
    return __builtin__.print(*args, **kwargs)

class DialogFlow:
    def __init__(self):
        if os.path.exists("data/mlp_model.pkl"):
            self.mlp, self.id_dict = pickle.load("data/mlp_model.pkl")
        else:
            self.mlp, self.id_dict = mlp("data/dialog_acts.dat")
        self.eInfo = ExtractInfo()
        self.dtree = DecisionTree()
        self.kAlgorithm = KeywordAlgorithm()
        self.extract = Extract()
        self.configurations = self.extract.extract_settings()

    def Welcome(self):
        """
        Starts the dialog, and begins the state transitioning function.
        """
        print("Hello, welcome to our restaurant system. What kind of restaurant are you looking for? You can ask for restaurants by area, price range or food type.")
        firstmsg = input()
        if (firstmsg == "settings"):
            self.configurateSettings()
        else:
            # TODO: replace each predict?
            first_msg_classification = self.dtree.predict(firstmsg) #"inform"
            if first_msg_classification in ["inform", "hello", "thankyou"]:
                query = self.kAlgorithm.keywordAlgorithm(firstmsg)
                self.checkQuery(query)
            elif first_msg_classification == "bye":
                self.Goodbye()

    def checkQuery(self, query):
        """
        Checks whether the current query still has enough available restaurant options.
        """
        solutions = self.eInfo.extract_info("data/restaurant_info.csv", query)
        print(len(solutions))
        print(query)
        if len(solutions) == 0:
            self.alternativeSuggestions(query)
        if len(solutions) == 1 or len(query) == 3:
            if "pricerange" not in query:
                query["pricerange"] = "dontcare"
            if "food" not in query:
                query["food"] = "dontcare"
            if "area" not in query:
                query["area"] = "dontcare"
            if len(solutions) == 1: print("There is only one restaurant available that satisfies your preferences:")
            self.getSuggestions(query)
        if len(solutions) > 1:
            self.getUserPreferences(query)

    def alternativeSuggestions(self, oldquery):
        """
        Offers alternative suggestions if there are none matching the (old) query.
        """
        print("There are no suggestions that satisfy your preferences. The following alternatives are available:")
        alternatives = []
        newquery = oldquery
        #PRICERANGE SUBSTITUTIONS
        if query["pricerange"] == "cheap":
            newquery["pricerange"] = "moderate"
            alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        elif query["pricerange"] == "moderate":
            newquery["pricerange"] = "expensive"
            alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        newquery = oldquery
        #AREA SUBSTITUTIONS
        if oldquery["area"] in ["centre", "north", "west"]:
            for area in ["centre", "north", "west"]:
                newquery["area"] = area
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        if oldquery["area"] in ["centre", "north", "east"]:
            for area in ["centre", "north", "east"]:
                newquery["area"] = area
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        if oldquery["area"] in ["centre", "south", "west"]:
            for area in ["centre", "south", "west"]:
                newquery["area"] = area
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        if oldquery["area"] in ["centre", "south", "east"]:
            for area in ["centre", "south", "east"]:
                newquery["area"] = area
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))

        #FOODTYPE SUBSTITUTIONS
        newquery = oldquery
        if oldquery["food"] in ["thai", "chinese", "korean", "vietnamese", "asian oriental"]:
            for food in ["thai", "chinese", "korean", "vietnamese", "asian oriental"]:
                newquery["food"] = food
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        if oldquery["food"] in ["mediterranean", "spanish", "portuguese", "italian", "romanian", "tuscan", "catalan"]:
            for food in ["mediterranean", "spanish", "portuguese", "italian", "romanian", "tuscan", "catalan"]:
                newquery["food"] = food
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        if oldquery["food"] in ["french", "european", "bistro", "swiss", "gastropub", "traditional"]:
            for food in ["french", "european", "bistro", "swiss", "gastropub", "traditional"]:
                newquery["food"] = food
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        if oldquery["food"] in ["north american", "steakhouse", "british"]:
            for food in ["north american", "steakhouse", "british"]:
                newquery["food"] = food
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        if oldquery["food"] in ["lebanese", "turkish", "persian"]:
            for food in ["lebanese", "turkish", "persian"]:
                newquery["food"] = food
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
        if oldquery["food"] in ["international", "modern european", "fusion"]:
            for food in ["international", "modern european", "fusion"]:
                newquery["food"] = food
                alternatives.append(self.eInfo.extract_info("data/restaurant_info.csv", newquery))
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
            self.restatePreferences(oldquery)
        if input == 2:
            suggindex = input("Which suggestion would you like?")
            self.giveInformation(suggestions, suggindex)

    def restatePreferences(self, query):
        """
        Allows the user to modify their query if something is wrong.
        """
        wrong = input("Which of the following would you like to change? \n 1. Price range \n 2. Food type \n 3. Area")
        if wrong == "1":
            query = {**query, **self.kAlgorithm.keywordAlgorithm(input("In what price range are you looking?"), mode="pricerange")}
        elif wrong == "2":
            query = {**query, **self.kAlgorithm.keywordAlgorithm(input("For what type of food are you looking?"), mode="food")}
        elif wrong == "3":
            query = {**query, **self.kAlgorithm.keywordAlgorithm(input("In what area are you looking?"), mode="area")}
        self.getSuggestions(query)

    def configurateSettings(self):
        """
        Allows changing of settings.
        """
        settings = self.extract.extract_settings()
        self.configurations['RESPONSE_DELAY']['value'] = 'false'

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
                self.extract.change_setting(settings)
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

    def getUserPreferences(self, query):
        """
        Finds out what type of restaurant the user is looking for.
        """
        if "pricerange" not in query.keys():
            query = {**query, **self.kAlgorithm.keywordAlgorithm(input("In what price range are you looking?"), mode="pricerange")}
            self.checkQuery(query)
            return
        if "food" not in query.keys():
            query = {**query, **self.kAlgorithm.keywordAlgorithm(input("For what type of food are you looking?"), mode="food")}
            self.checkQuery(query)
            return
        if "area" not in query.keys():
            query = {**query, **self.kAlgorithm.keywordAlgorithm(input("In what area are you looking?"), mode="area")}
            self.checkQuery(query)
            return

        #checkPreferences(query)

    def checkPreferences(self, query):
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
        if self.dtree.predict(msg) in ["negate", "deny"]:
            wrong = input("Which of the following is wrong? \n 1. Price range \n 2. Food type \n 3. Area")
            if wrong == "1":
                query = {**query, **self.kAlgorithm.keywordAlgorithm(input("In what price range are you looking?"), mode = "pricerange")}
            elif wrong == "2":
                query = {**query, **self.kAlgorithm.keywordAlgorithm(input("For what type of food are you looking?"), mode="food")}
            elif wrong == "3":
                query = {**query, **self.kAlgorithm.keywordAlgorithm(input("In what area are you looking?"), mode="area")}
            self.checkPreferences(query)
        elif self.dtree.predict(msg) in ["affirm", "thankyou"]:
            self.getSuggestions(query)
        else:
            print("Sorry, I didn't understand that.")
            self.checkPreferences(query)

    def getExtraPreferences(self, suggestions, query):
        satisfied = False
        additional_pref = []
        
        while not satisfied:
            fmsg = input("would you like to add more preferences?")

            if self.dtree.predict(fmsg) in ["negate", "deny"]:
                print("Let's see which restaurants are in accorandence with your wishes.")
                satisfied = True
            elif self.dtree.predict(fmsg) in ["affirm", "thankyou"]:
                smsg = input("What would you like to add? Choose one of the following options.\n 1. (not) busy \n 2. duration of your visit \n 3. child friendly \n 4. romantic \n 5. serves fast food \n 6. quality of the restaurant \n 7. suitable for a date \n 8. vegetarian options")
                if smsg == "1":
                    choice = input("Do want a restaurant that is busy?").lower()
                    if self.dtree.predict(choice) in ["affirm", "thankyou"]:
                        additional_pref += ["busy"]
                        print("You want a restaurant that is busy.")
                    elif self.dtree.predict(choice) in ["negate", "deny"]:
                        additional_pref += ["not busy"]
                        print("You want a restaurant that is not busy.")
                    else: 
                        print("Sorry I did not get that. Please try again.")
                elif smsg == "2":
                    choice = input("Would you like to spend a lot of time in the restaurant?").lower()
                    if self.dtree.predict(choice) in ["affirm", "thankyou"]:
                        additional_pref += ["long time"]
                        print("You want to spend a long time at the restaurant.")
                    elif self.dtree.predict(choice) in ["negate", "deny"]:
                        additional_pref += ["not long time"]
                        print("You do not want to spend a long time at the restaurant.")
                    else:
                        print("Sorry I did not get that. Please try again.")
                elif smsg == "3":
                    additional_pref += ["children"]
                    print("You are looking for a restaurant that is child friendly.")
                elif smsg == "4":
                    additional_pref += ["romantic"]
                    print("You are looking for a restaurant that is romantic.")
                elif smsg == "5":
                    choice = input("Would you like a restaurant that serves fast food?").lower()
                    if self.dtree.predict(choice) in ["affirm", "thankyou"]:
                        additional_pref += ["fast food"]
                        print("You are looking for a restaurant that serves fast food.")
                    elif self.dtree.predict(choice) in ["negate", "deny"]:
                        additional_pref += ["no fast food"]
                        print("You are looking for a restaurant that does not serve fast food.")
                    else:
                        print("Sorry I did not get that. Please try again.")
                elif smsg == "6":
                    choice = input("Are you looking for a high quality restaurant?").lower()
                    if self.dtree.predict(choice) in ["affirm", "thankyou"]:
                        additional_pref += ["good restaurant"]
                        print("You are looking for a good restaurant.")
                    elif self.dtree.predict(choice) in ["negate", "deny"]:
                        additional_pref += ["bad restaurant"]
                        print("You are looking for a bad restaurant.")
                    else:
                        print("Sorry I did not get that. Please try again.")
                        self.getExtraPreferences(suggestions, query)
                elif smsg == "7":
                    additional_pref += ["date"]
                    print("You are looking for a restaurant that is suitable for a date.")
                elif smsg == "8":
                    additional_pref += ["vegetarian"]
                    print("You are looking for a restaurant that has vegetarian options.")
                elif self.dtree.predict(smsg) in ["negate", "deny", "reqalts", "reqmore"]:
                        print("Unfortunately, you can only choose one of the additional preferences above.")
                else:
                    print("Sorry I did not understand that. Please try again")
            else:
                print("Sorry I didn't understand that. Please try again.") 
        
        new_suggestions = implications(additional_pref, query)
        
        i = 0
        for restaurant in suggestions:
            if suggestions[i] in new_suggestions: #check if restaurant is still suitable after adding new preferences
                interested = input(suggestions.iloc[i]['restaurantname'] + " meets all your preferences \n Are you interested in this restaurant?").lower()
                if self.dtree.predict(interested) in ["affirm", "thankyou"]:
                    self.giveInformation(suggestions, i)
                else:
                    print("No problem, let's continue.")
            else:
                print(suggestions.iloc[i]['restaurantname'] + " does not meet all your preferences")
            i += 1
        
        print("There are no restaurants left. PLease try again.")
        self.getExtraPreferences(suggestions, query)
        
    def getSuggestions(self, query):
        """
        Retrieves the suggestions from the database, given our user input.
        """
        suggestions = self.eInfo.extract_info("data/restaurant_info.csv", query)
        if len(suggestions) > 1:
            self.getExtraPreferences(suggestions, query)
        
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
            if self.dtree.predict(choice) in ["affirm", "thankyou"]:
                satisfied = True
            elif self.dtree.predict(choice) in ["negate", "deny", "reqalts", "reqmore"]:
                i += 1
                #print("Looking for alternatives...")
            else:
                print("Sorry, I didn't catch that. Please try again.")
        if not satisfied:
            print("Sadly we have no restaurants available that match your preferences. Try again. \n")
            self.Welcome()
            return

        self.giveInformation(suggestions, i)

    def giveInformation(self, suggestions, suggestionIndex):
        """
        Asks whether the user needs extra information, and provides it where necessary.
        """
        satisfied = 0
        while not satisfied:
            more_info = input("Would you like some more information about the restaurant?")
            if self.dtree.predict(more_info) in ["affirm", "thankyou"]:
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
            elif self.dtree.predict(more_info) in ["negate", "deny"]:
                satisfied = True
            else:
                print("Sorry, I didn't catch that. Please try again.")
        self.Goodbye(suggestions.iloc[suggestionIndex]['restaurantname'])

    def Goodbye(self, restaurantname = ""):
        """
        Ends the dialog.
        """
        if restaurantname != "":
            print("We hope you have a great meal at " + restaurantname + "!")
        else: print("Goodbye!")