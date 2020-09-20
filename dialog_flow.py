"""
dictionary pricerange area food van Eddie

wij sturen dictionary =(query)

krijgen van Bence een lijst van dictionaries (zoals in .csv) met suggesties
(of lege lijst) het kan zijn dat sommige gegevens leeg zijn: dan none.
"""
import pandas as pd
import re
from keyword_algorithm import keywordAlgorithm
from extract_info import extract_info
import decision_tree as dt
#dtree = dt.createDecisionTree()
def Welcome():
    print("Hello, welcome to our restaurant system. What kind of restaurant are you looking for? You can ask for restaurants by area, price range or food type.")
    firstmsg = input()
    first_msg_classification = "inform" #dt.predict(firstmsg, dtree)
    if first_msg_classification in ["inform", "hello", "thankyou"]:
        getUserPreferences(firstmsg)
    if first_msg_classification == "bye":
        Goodbye()


def getUserPreferences(message):
    query = keywordAlgorithm(message)
    if "pricerange" not in query.keys():
        query = {**query, **keywordAlgorithm(input("In what price range are you looking?"), mode="pricerange")}
    if "food" not in query.keys():
        query = {**query, **keywordAlgorithm(input("For what type of food are you looking?"), mode="food")}
    if "area" not in query.keys():
        query = {**query, **keywordAlgorithm(input("In what area are you looking?"), mode="area")}

    checkPreferences(query)

def checkPreferences(query):
    print("You are looking for a restaurant", end="")
    if not query["pricerange"] == "dontcare":
        print(" in the " + query["pricerange"] + " pricerange", end="")
    if not query["food"] == "dontcare":
        print(" that serves " + query["food"], end="")
    if not query["area"] == "dontcare":
        print(" in the " + query["area"] + " of town", end="")
    print(". Is this correct? Type yes or no.")
    if input().lower() == "no":
        wrong = input("Which of the following is wrong? \n 1. Price range \n 2. Food type \n 3. Area")
        if wrong == "1":
            query = {**query, **keywordAlgorithm(input("In what price range are you looking?"), mode = "pricerange")}
        elif wrong == "2":
            query = {**query, **keywordAlgorithm(input("For what type of food are you looking?"), mode="food")}
        elif wrong == "3":
            query = {**query, **keywordAlgorithm(input("In what area are you looking?"), mode="area")}
        checkPreferences(query)
    else: getSuggestions(query)



def getSuggestions(query):
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
            "Are you interested in this restaurant or would you like an alternative? Type 1 to continue, 2 for an alternative.")
        if choice == "1":
            satisfied = True
        elif choice == "2":
            i += 1
        else:
            print("Sorry, I didn't catch that. Please try again.")
    if not satisfied:
        print("Sadly we have no restaurants available that match your preferences. Try again. \n")
        Welcome()
        return

    giveInformation(suggestions, i)

def giveInformation(suggestions, suggestionIndex):
    satisfied = 0
    while not satisfied:
        choice = input("Would you like some more information about: \n 1. Phone number \n 2. Address \n 3. No information needed.")
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
        elif choice == "3":
            satisfied = True
        else:
            print("Sorry, I didn't catch that. Please try again.")
    Goodbye(suggestions.iloc[suggestionIndex]['restaurantname'])

def Goodbye(restaurantname = ""):
    if restaurantname != "":
        print("We hope you have a great meal at " + restaurantname + "!")
    else: print("Goodbye!")

Welcome()