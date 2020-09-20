"""
dictionary pricerange area food van Eddie

wij sturen dictionary =(query)

krijgen van Bence een lijst van dictionaries (zoals in .csv) met suggesties
(of lege lijst) het kan zijn dat sommige gegevens leeg zijn: dan none.
"""
def FlowControl():
    print("Hello, welcome to our restaurant system. To help you, we need some information about the restaurant you're looking for.")
    query = AskInfo()
    # if input("You are looking for a restaurant in the " + query["pricerange"]
    #       + " pricerange, that serves " + query["food"] + " food in the " + query["area"] + " of the city. Is this correct? Type yes or no.").lower() == "no":
    #     wrong = input("Which of the following is wrong? \n 1. Price range \n 2. Food type \n 3. Area")
    #     if wrong == 1:
    #         input() #Dit kunnen we niet doen, is deel van keyword matching.
    suggestions = GetSuggestions(query) #moet random geshuffled zijn, of nog geshuffled worden
    i = 0
    satisfied = False
    while len(suggestions) > i and not satisfied:
        print(suggestions[i]['restaurantname'] + " is a nice place", end= " ")
        if suggestions[i]["area"] != None: print("in the " + suggestions[i]["area"] + " of town", end= " ")
        if suggestions[i]["pricerange"] != None: print("in the " + suggestions[i]["pricerange"] + " pricerange", end= "")
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
        FlowControl()
    satisfied = 0
    while not satisfied:
        choice = input("Would you like some more information about: \n 1. Phone number \n 2. Address \n 3. No information needed.")
        if choice == "1":
            print("The phone number is " + suggestions[i]["phone"] + ".")
        elif choice == "2":
            print("The address is " + suggestions[i]["addr"] + " " + suggestions[i]["postcode"]+ ".")
        elif choice == "3":
            satisfied = True
        else:
            print("Sorry, I didn't catch that. Please try again.")
    print("We hope you have a great meal at " + suggestions[i]['restaurantname'] + "!")



def GetSuggestions(query):
    return ([{"restaurantname":"saint johns chop house", "pricerange":"moderate", "area":"west","food":"british","phone": "01223 353110", "addr": "21 - 24 northampton street", "postcode":"c.b 3"}])
def AskInfo():
    return ({"pricerange":"moderate", "area":"west",
            "food":"italian"})

FlowControl()