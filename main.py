from extract import Extract
from baseline_systems import BaseLineSystem
from decision_tree import DecisionTree
from dialog_flow import DialogFlow
from mlp import mlp, mlp_test

def main():
    baseLineSystem = BaseLineSystem()
    # List of commands
    print("Type one of the following numbers to execute the command: ")
    print("1. test baseline")
    print("2. test decision tree")
    print("3. test neural network")
    print("4. baseline")
    print("5. decision tree")
    print("6. neural network")
    print("7. dialog")

    userInput = input("> ")

    if userInput == '1':
        data = Extract("data/dialog_acts.dat")
        baseLineSystem.testBaselines(data)
    elif userInput == '2':
        dt = DecisionTree()
        dt.preformDecisionTree('test')
    elif userInput == '3':
        mlp("data/dialog_acts.dat")
    elif userInput == '4':
        classify_user_input()
    elif userInput == '5':
        dt = DecisionTree()
        dt.preformDecisionTree('')
    elif userInput == '6':
        print("Currently not implemented.")
    elif userInput == '7':
        dialogFlow = DialogFlow()
        dialogFlow.Welcome()
        # See mlp_test for explanation.
        # model, id_dict = mlp("dialog_acts.dat")
        # print("You can quit by typing 'stop'.")
        # while True:
        #     sentence = input("Please write your sentence here:\n")
        #     if sentence == "stop":
        #         break
        #     prediction = mlp_test(model, sentence, id_dict)
        #     print(f"We predict your sentence belongs to the {prediction} class.")

def classify_user_input():
    data = Extract("data/dialog_acts.dat")
    
    # Classifies input from the user into a certain dialog act group.  
    
    sentence = (str(input('Enter sentence: '))).lower().split()
    
    if (len(sentence) > 0):
        print('Majority classification is: '  + baseLineSystem.majority_baseline(data)[0])
        print('Rule based classification is: '  + baseLineSystem.rule_based_baseline(sentence)[0])

main()