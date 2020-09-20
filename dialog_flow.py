"""
dictionary pricerange area food van Eddie

wij sturen dictionary =(query)

krijgen van Bence een lijst van dictionaries (zoals in .csv) met suggesties
(of lege lijst) het kan zijn dat sommige gegevens leeg zijn: dan none.
"""
import pandas as pd
from extract_info import extract_info
def flowControl():
    print("Hello, welcome to our restaurant system. What kind of restaurant are you looking for? You can ask for restaurants by area, price range or food type.")
    query = extract_info()
     if input("You are looking for a restaurant in the " + query["pricerange"]
           + " pricerange, that serves " + query["food"] + " food in the " + query["area"] + " of the city. Is this correct? Type yes or no.").lower() == "no":
        wrong = input("Which of the following is wrong? \n 1. Price range \n 2. Food type \n 3. Area")
         if wrong == 1:
             input() #Dit kunnen we niet doen, is deel van keyword matching.
    suggestions = extract_info("restaurant_info.csv", query) #moet random geshuffled zijn, of nog geshuffled worden
    i = 0
    satisfied = False
    while len(suggestions) > i and not satisfied:
        print(suggestions.iloc[i]['restaurantname'] + " is a nice place", end= " ")
        if not suggestions.iloc[[i]]["area"].empty: print("in the " + suggestions.iloc[i]["area"] + " of town", end= " ")
        if not suggestions.iloc[[i]]["pricerange"].empty: print("in the " + suggestions.iloc[i]["pricerange"] + " pricerange", end= "")
        print(".")
        choice = input("Are you interested in this restaurant or would you like an alternative? Type 1 to continue, 2 for an alternative.")
        if choice == "1":
            satisfied = True
        elif choice == "2":
            i += 1
        else:
            print("Sorry, I didn't catch that. Please try again.")
    if not satisfied:
        print("Sadly we have no restaurants available that match your preferences. Try again. \n")
        flowControl()
        return
    satisfied = 0
    while not satisfied:
        choice = input("Would you like some more information about: \n 1. Phone number \n 2. Address \n 3. No information needed.")
        if choice == "1":
            if suggestions.iloc[[i]]["phone"].empty:
                print("Sadly we have no phone number available for this restaurant.")
            else: print("The phone number is " + suggestions.iloc[i]["phone"] + ".")
        elif choice == "2":
            if suggestions.iloc[[i]]["addr"].empty or suggestions.iloc[[i]]["postcode"].empty:
                print("The address is " + suggestions.iloc[i]["addr"] + " " + suggestions.iloc[i]["postcode"] + ".")
        elif choice == "3":
            satisfied = True
        else:
            print("Sorry, I didn't catch that. Please try again.")
    print("We hope you have a great meal at " + suggestions.iloc[i]['restaurantname'] + "!")



def GetSuggestions(query):
    return ([{"restaurantname":"saint johns chop house", "pricerange":"moderate", "area":"west","food":"british","phone": "01223 353110", "addr": "21 - 24 northampton street", "postcode":"c.b 3"}])
def AskInfo():
    return ({"pricerange":"moderate", "area":"west",
            "food":"italian"})

flowControl()