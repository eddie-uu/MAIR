from __future__ import print_function
from keyword_algorithm import keyword_algorithm
from decision_tree import decision_tree
from mlp import multi_layer_perceptron
from extract_info import extract_info
from extract import extract
from imply import Implications
import nltk
import time
import pandas as pd
import re
import json
import random
import pickle
import os
import sys


"""
This file controls the main dialog flow. A typical dialog will have the following flow:
Welcome():                      A Welcome message welcoming the user and asking for an input.
getUserPreferences:             The user will give their preferences for the restaurant they are looking for.
                                These preferences include pricerange, food, and area, but not secondary preferences like
                                child-friendly, romantic or good food.
checkPreferences:               Confirms the given preferences with the user.
getExtraPreferences (optional): The user gives their additional preferences. (child-friendly, romantic, good food, etc.)
getSuggestions:                 The user is presented with the restaurants that match the user's preferences. The user then decides
                                which restaurant he/she is interested in.
askExtraInfo:                   The dialog system asks if the user wants any additional information,
                                options being phone number and address.
giveInformation (optional):     The dialog system gives the requested information to the user.
Goodbye:                        Wishes the user a nice meal at the chosen restaurant, or says goodbye if the user stops
                                the conversation.
                                
Notice that some of these are optional, and there are some extra helper functions, but also dialog steps that are not always shown.
alternativeSuggestions, for example, is only called when the query of the user results in 0 matches.
getExtraPreferences is optional, because a query given by the user might not result in more than one matches.
In that case, the only suggestion, or alternative suggestions will be given and no extra preferences will be asked.
giveInformation is of course optional, if the user decided that he does not need any information about the restaurant.

There are some edge dialog cases, where some functions are repeated or called multiple times. For example, a user might want to
change their preferences in checkPreferences, in which case we will go back to getUserPreferences to make adjustments.
They might also want to change their extra preferences when the list of restaurants that satisfy their extra preferences
is not to their liking.
"""


try:
    import __builtin__
except ImportError:
    # Python 3
    import builtins as __builtin__

extractConfig = extract().extract_settings()

def input(prompt = ''):
    print(prompt)

    return __builtin__.input(">")

def print(*args, **kwargs):
    # Response delay if true in settings
    if extractConfig['RESPONSE_DELAY']['value'].lower() == 'true':
        time.sleep(1)

    # All caps output if true in settings
    for arg in args:
        if isinstance(arg, str) and extractConfig['OUTPUT_IN_CAPS']['value'].lower() == 'true':
            return __builtin__.print(arg.upper(), **kwargs)
    return __builtin__.print(*args, **kwargs)

class dialog_flow:
    def __init__(self):
        self.algorithm      = multi_layer_perceptron()
        self.eInfo          = extract_info()
        self.kAlgorithm     = keyword_algorithm()
        self.configurations = extract().extract_settings()
        
        if os.path.exists("data/mlp_model.pkl"):
            with open("data/mlp_model.pkl", 'rb') as f:
                self.mlp, self.id_dict, self.scaler = pickle.load(f)
        else:
            self.mlp, self.id_dict, self.scaler = self.algorithm.mlp("data/dialog_acts.dat")
            with open("data/mlp_model.pkl", 'wb') as f_pickle:
                pickle.dump((self.mlp, self.id_dict, self.scaler), f_pickle)

        if self.configurations["CURRENT_CLASSIFIER"]["value"] == "dt":
            self.algorithm = decision_tree()        
        

    def welcome(self):
        '''
        Starts the dialog, and begins the state transitioning function.
        '''

        first_msg = input("Hello, welcome to our restaurant system. What kind of restaurant are you looking for? You can ask for restaurants by area, price range or food type.")
        first_msg_classification = self.algorithm.predict(first_msg, self.mlp, self.scaler, self.id_dict)
        if first_msg_classification in ["inform", "thankyou", "request"]:
            query = self.kAlgorithm.keyword_algorithm(first_msg)
            self.__check_query(query)
        elif first_msg_classification == "bye":
            self.__goodbye()
        elif first_msg_classification == "hello":
            self.welcome()
        else:
            print("Sorry, I did not understand that.")
            self.welcome()


    def __check_query(self, query):
        '''
        Checks whether the current query still has enough available restaurant options.
        If the number of suggestions is 2 or higher, proceed normally by asking more preferences.
        If the number of suggestions is 1, or there are no other query options to ask (food, area and pricerange are all given),
        offer the matching restaurant(s).
        If the number of suggestions is 0, give the user alternative suggestions that are closely related to their given
        preferences.

        :param query: a dictionary extracted from the input given by the user. Example of a query:
                      {'pricerange': 'cheap', 'food': 'dontcare', 'area': 'center'}
                      NOTE: This parameter is present in multiple functions. For readability purposes, it will not be
                            re-explained in every function.
        '''
        solutions = self.eInfo.extract_info("data/restaurant_info.csv", query)
        if len(solutions) == 0:
            self.__alternative_suggestions(query, solutions)
        if len(solutions) == 1 or len(query) == 3:
            if "pricerange" not in query:
                query["pricerange"] = "dontcare"
            if "food" not in query:
                query["food"] = "dontcare"
            if "area" not in query:
                query["area"] = "dontcare"
            if len(solutions) == 1:
                print("There is only one restaurant available that satisfies your preferences:")
            self.__get_suggestions(query)
        if len(solutions) > 1:
            self.__get_user_preferences(query)

    def __alternative_suggestions(self, old_query, empty_frame):
        '''
        Offers alternative suggestions if there are none matching the (old) query.
        Example of how an alternative suggestion is determined: if the user is looking for a cheap restaurant,
        a moderately priced restaurant might also be acceptable.

        For a full list of substitutions, see 1c: Database information.

        :param empty_frame: an empty pandas frame with the correct column names. Does not do anything special, but creating a new
                           pandas dataframe with the correct column names is not very pretty.
        '''
        print("There are no suggestions that satisfy your preferences. Here are some alternatives:")
        alternatives = empty_frame
        new_query = old_query.copy()
        #PRICERANGE SUBSTITUTIONS
        if "pricerange" in old_query.keys():
            if old_query["pricerange"] == "cheap":
                new_query["pricerange"] = "moderate"
                alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
            elif old_query["pricerange"] == "moderate":
                new_query["pricerange"] = "expensive"
                alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
        new_query = old_query.copy()
        #AREA SUBSTITUTIONS
        if "area" in old_query.keys():
            if old_query["area"] in ["centre", "north", "west"]:
                for area in ["centre", "north", "west"]:
                    new_query["area"] = area
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
            if old_query["area"] in ["centre", "north", "east"]:
                for area in ["centre", "north", "east"]:
                    new_query["area"] = area
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
            if old_query["area"] in ["centre", "south", "west"]:
                for area in ["centre", "south", "west"]:
                    new_query["area"] = area
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
            if old_query["area"] in ["centre", "south", "east"]:
                for area in ["centre", "south", "east"]:
                    new_query["area"] = area
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])

        #FOODTYPE SUBSTITUTIONS
        new_query = old_query.copy()
        if "food" in old_query.keys():
            if old_query["food"] in ["thai", "chinese", "korean", "vietnamese", "asian oriental"]:
                for food in ["thai", "chinese", "korean", "vietnamese", "asian oriental"]:
                    new_query["food"] = food
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
            if old_query["food"] in ["mediterranean", "spanish", "portuguese", "italian", "romanian", "tuscan", "catalan"]:
                for food in ["mediterranean", "spanish", "portuguese", "italian", "romanian", "tuscan", "catalan"]:
                    new_query["food"] = food
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
            if old_query["food"] in ["french", "european", "bistro", "swiss", "gastropub", "traditional"]:
                for food in ["french", "european", "bistro", "swiss", "gastropub", "traditional"]:
                    new_query["food"] = food
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
            if old_query["food"] in ["north american", "steakhouse", "british"]:
                for food in ["north american", "steakhouse", "british"]:
                    new_query["food"] = food
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
            if old_query["food"] in ["lebanese", "turkish", "persian"]:
                for food in ["lebanese", "turkish", "persian"]:
                    new_query["food"] = food
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
            if old_query["food"] in ["international", "modern european", "fusion"]:
                for food in ["international", "modern european", "fusion"]:
                    new_query["food"] = food
                    alternatives = pd.concat([alternatives, self.eInfo.extract_info("data/restaurant_info.csv", new_query)])
        alternatives = alternatives.sample(frac=1).drop_duplicates()
        not_satisfied = True
        begin_index = 0
        end_index = int(self.configurations["ALTERNATIVES_NUMBER"]["value"])
        if len(alternatives) == 0:
            print("We could not find any alternatives for your query. Your input was undecipherable.")
            self.welcome()
            return
        while not_satisfied:
            if end_index > len(alternatives):
                for i in range(begin_index, len(alternatives)):
                    self.__offer_restaurant(alternatives, i)
            else:
                for i in range(begin_index, end_index):
                    self.__offer_restaurant(alternatives, i)
            print("Do you want to:")
            print("1. Change your preferences")
            print("2. Choose one of these alternatives")
            if len(alternatives) > end_index:
                print("3. Request other alternatives")
            inp = input()
            if inp == "1":
                self.__restate_preferences(old_query)
                not_satisfied = False
            if inp == "2":
                suggindex = input("Which suggestion would you like?")
                self.__ask_extra_info(alternatives, int(suggindex) - 1)
                not_satisfied = False
            if len(alternatives) > end_index:
                if inp == "3":
                    begin_index += int(self.configurations["ALTERNATIVES_NUMBER"]["value"])
                    end_index += int(self.configurations["ALTERNATIVES_NUMBER"]["value"])


    def __offer_restaurant(self, restaurantList, index):
        '''
        Offers (via printing to console) a selected restaurant to the user.

        :param restaurantList: a pandas dataframe with restaurants.
        :param index: the index of the selected restaurant.
        '''
        print(str(index + 1) + ": ", end="")
        print(str(restaurantList.iloc[index]["restaurantname"]) + " is a nice place", end=" ")
        if not restaurantList.iloc[[index]]["food"].empty: print("serving " + str(restaurantList.iloc[index]["food"]), end=" ")
        if not restaurantList.iloc[[index]]["area"].empty: print("in the " + str(restaurantList.iloc[index]["area"]) + " of town", end=" ")
        if not restaurantList.iloc[[index]]["pricerange"].empty: print(
               "in the " + str(restaurantList.iloc[index]["pricerange"]) + " pricerange", end="")
        print(".")

    def __restate_preferences(self, query):
        '''
        Allows the user to modify their query if something is wrong.
        '''

        wrong = input("Which of the following would you like to change? \n 1. Price range \n 2. Food type \n 3. Area")
        if wrong == "1":
            query = {**query, **self.kAlgorithm.keyword_algorithm(input("In what price range are you looking?"), mode="pricerange")}
        elif wrong == "2":
            query = {**query, **self.kAlgorithm.keyword_algorithm(input("For what type of food are you looking?"), mode="food")}
        elif wrong == "3":
            query = {**query, **self.kAlgorithm.keyword_algorithm(input("In what area are you looking?"), mode="area")}
        self.__get_suggestions(query)

    def __get_user_preferences(self, query):
        '''
        Finds out what type of restaurant the user is looking for, by asking every possible preference and checking if the query
        still has enough matches.
        '''
        if "pricerange" not in query.keys():
            query = {**query, **self.kAlgorithm.keyword_algorithm(input("In what price range are you looking?"), mode="pricerange")}
            self.__check_query(query)
            return
        if "food" not in query.keys():
            query = {**query, **self.kAlgorithm.keyword_algorithm(input("For what type of food are you looking?"), mode="food")}
            self.__check_query(query)
            return
        if "area" not in query.keys():
            query = {**query, **self.kAlgorithm.keyword_algorithm(input("In what area are you looking?"), mode="area")}
            self.__check_query(query)
            return


    def __check_preferences(self, query):
        '''
        Confirms the retrieved preferences with the user, and modifies them if needed.
        '''
        print("You are looking for a restaurant", end="")
        if not query["pricerange"] == "dontcare":
            print(" in the " + query["pricerange"] + " pricerange", end="")
        if not query["food"] == "dontcare":
            print(" that serves " + query["food"], end="")
        if not query["area"] == "dontcare":
            print(" in the " + query["area"] + " of town", end="")
        print(". Is this correct? Type yes or no.")
        msg = input().lower()
        if self.algorithm.predict(msg, self.mlp, self.scaler, self.id_dict) in ["negate", "deny"]:
            wrong = input("Which of the following is wrong? \n 1. Price range \n 2. Food type \n 3. Area")
            if wrong == "1":
                query = {**query, **self.kAlgorithm.keyword_algorithm(input("In what price range are you looking?"), mode = "pricerange")}
            elif wrong == "2":
                query = {**query, **self.kAlgorithm.keyword_algorithm(input("For what type of food are you looking?"), mode="food")}
            elif wrong == "3":
                query = {**query, **self.kAlgorithm.keyword_algorithm(input("In what area are you looking?"), mode="area")}
            self.__check_preferences(query)
        elif self.algorithm.predict(msg, self.mlp, self.scaler, self.id_dict) in ["affirm", "thankyou"]:
            self.__get_suggestions(query)
        else:
            print("Sorry, I didn't understand that.")
            self.__check_preferences(query)

    def __get_extra_preferences(self, suggestions, query, again=False):
        '''
        Determines the user's extra preferences, such as romantic, fast food, for children or long time.

        :param suggestions: List of suggestions that match the base preferences (food, area, pricerange).
        :param again:       If the user wants to give different preferences, this function is started "again", and we want
                            a different starting message.
                            "Would you like to try some different preferences?" vs "Would you like to add more preferences?".
        '''
        satisfied = False
        additional_pref = []
        
        while not satisfied:
            if again:
                fmsg = input("Would you like to try some different preferences?")
                again = False
            else:
                fmsg = input("Would you like to add more preferences?")
            if self.algorithm.predict(fmsg, self.mlp, self.scaler, self.id_dict) in ["negate", "deny"]:
                print("Let's see which restaurants are in accordance with your wishes.")
                satisfied = True
            elif self.algorithm.predict(fmsg, self.mlp, self.scaler, self.id_dict) in ["affirm", "thankyou"]:
                smsg = input("What would you like to add? Choose one of the following options.\n 1. (not) busy \n 2. duration of your visit \n 3. child friendly \n 4. romantic \n 5. serves fast food \n 6. quality of the restaurant \n 7. suitable for a date \n 8. vegetarian options")
                if smsg == "1":
                    choice = input("Do want a restaurant that is busy?").lower()
                    if self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["affirm", "thankyou"]:
                        additional_pref += ["busy"]
                        print("You want a restaurant that is busy.")
                    elif self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["negate", "deny"]:
                        additional_pref += ["not busy"]
                        print("You want a restaurant that is not busy.")
                    else: 
                        print("Sorry I did not get that. Please try again.")
                elif smsg == "2":
                    choice = input("Would you like to spend a lot of time in the restaurant?").lower()
                    if self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["affirm", "thankyou"]:
                        additional_pref += ["long time"]
                        print("You want to spend a long time at the restaurant.")
                    elif self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["negate", "deny"]:
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
                    if self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["affirm", "thankyou"]:
                        additional_pref += ["fast food"]
                        print("You are looking for a restaurant that serves fast food.")
                    elif self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["negate", "deny"]:
                        additional_pref += ["no fast food"]
                        print("You are looking for a restaurant that does not serve fast food.")
                    else:
                        print("Sorry I did not get that. Please try again.")
                elif smsg == "6":
                    choice = input("Are you looking for a high quality restaurant?").lower()
                    if self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["affirm", "thankyou"]:
                        additional_pref += ["good restaurant"]
                        print("You are looking for a good restaurant.")
                    elif self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["negate", "deny"]:
                        additional_pref += ["bad restaurant"]
                        print("You are looking for a bad restaurant.")
                    else:
                        print("Sorry I did not get that. Please try again.")
                        self.__get_extra_preferences(suggestions, query)
                elif smsg == "7":
                    additional_pref += ["date"]
                    print("You are looking for a restaurant that is suitable for a date.")
                elif smsg == "8":
                    additional_pref += ["vegetarian"]
                    print("You are looking for a restaurant that has vegetarian options.")
                elif self.algorithm.predict(smsg, self.mlp, self.scaler, self.id_dict) in ["negate", "deny", "reqalts", "reqmore"]:
                        print("Unfortunately, you can only choose one of the additional preferences above.")
                else:
                    print("Sorry I did not understand that. Please try again")
            else:
                print("Sorry I didn't understand that. Please try again.")
        quality_types = ["bad food", "mediocre food", "good food"]
        for quality in quality_types:
            if quality in additional_pref:
                additional_pref.remove(quality)
                query["quality"] = quality
        imply = Implications()
        new_suggestions = imply(additional_pref, query)
        for i in range(len(suggestions)):
            not_understood = True
            if str(suggestions.iloc[i]["restaurantname"]) in new_suggestions["restaurantname"].tolist(): #check if restaurant is still suitable after adding new preferences
                while not_understood:
                    interested = input(suggestions.iloc[i]['restaurantname'] + " meets all your preferences \n Are you interested in this restaurant?").lower()
                    if self.algorithm.predict(interested, self.mlp, self.scaler, self.id_dict) in ["affirm", "thankyou"]:
                        self.__ask_extra_info(suggestions, i)
                        return
                    elif self.algorithm.predict(interested, self.mlp, self.scaler, self.id_dict) in ["negate", "deny"]:
                        print("No problem, let's continue.")
                        not_understood = False
                    else:
                        print("Sorry, we couldn't understand.")
        print("There are no restaurants left.", end = " ")

        self.__get_extra_preferences(suggestions, query, True)
        
    def __get_suggestions(self, query):
        '''
        Retrieves the suggestions from the database that match the preferences of the user. This function only works for
        the base preferences (food, area, pricerange). For the extra preferences, see the imply.py file.
        '''
        suggestions = self.eInfo.extract_info("data/restaurant_info.csv", query)
        satisfied = False
        if len(suggestions) > 1:
            self.__get_extra_preferences(suggestions, query)
            satisfied = True
        i = 0

        while len(suggestions) > i and not satisfied:
            self.__offer_restaurant(suggestions, i)
            choice = input(
                "Are you interested in this restaurant?")
            if self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["affirm", "thankyou"]:
                satisfied = True
                self.__ask_extra_info(suggestions, i)
            elif self.algorithm.predict(choice, self.mlp, self.scaler, self.id_dict) in ["negate", "deny", "reqalts", "reqmore"]:
                i += 1
            else:
                print("Sorry, I didn't catch that. Please try again.")
        if not satisfied:
            print("Sadly we have no restaurants available that match your preferences. Try again. \n")
            self.welcome()
            return


    def __ask_extra_info(self, suggestions, suggestion_index):
        '''
        Asks whether the user needs extra information about the selected restaurant, and which information is desired.
        Parameters are used to identify the selected restaurant.

        :param suggestions:     List of suggestions.
        :param suggestion_index: Index of the selected restaurant.
        '''
        satisfied = 0
        while not satisfied:
            more_info = input("Would you like some more information about the restaurant?").lower()
            if "phone number" in more_info:
                self.__give_information(suggestions, suggestion_index, "1")
            elif "address" in more_info or "postcode" in more_info:
                self.__give_information(suggestions, suggestion_index, "2")
            elif self.algorithm.predict(more_info, self.mlp, self.scaler, self.id_dict) in ["affirm", "thankyou"]:
                choice = input("What information would you like to have? \n 1. Phone number \n 2. Address.")
                self.__give_information(suggestions, suggestion_index, choice)
            elif self.algorithm.predict(more_info, self.mlp, self.scaler, self.id_dict) in ["negate", "deny"]:
                satisfied = True
            else:
                print("Sorry, I didn't catch that. Please try again. Try answering \"yes\" or \"no\"")
        self.__goodbye(suggestions.iloc[suggestion_index]['restaurantname'])

    def __give_information(self, suggestions, suggestion_index, choice):
        '''
        Gives the requested information about the selected restaurant.

        NOTE: address and postcode are merged, since it does not make sense to only want one of the two.
        :param choice: 1 for phone number, 2 for address.
        '''
        if choice == "1":
            if suggestions.iloc[[suggestion_index]]["phone"].empty:
                print("Sadly we have no phone number available for this restaurant.")
            else:
                print("The phone number is " + suggestions.iloc[suggestion_index]["phone"] + ".")
        elif choice == "2":
            if suggestions.iloc[[suggestion_index]]["addr"].empty or suggestions.iloc[[suggestion_index]][
                "postcode"].empty:
                print("Sadly we have no address available for this restaurant.")
            else:
                print("The address is " + str(suggestions.iloc[suggestion_index]["addr"]) + " " +
                      str(suggestions.iloc[suggestion_index]["postcode"]) + ".")

    def __goodbye(self, restaurantname=""):
        """
        Ends the dialog.
        """
        if restaurantname != "":
            print("We hope you have a great meal at " + restaurantname + "!")
        else: print("Goodbye!")
        sys.exit()