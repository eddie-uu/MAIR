from extract import extract_data
from baseline_systems import majority_baseline
from baseline_systems import rule_based_baseline
from baseline_systems import testBaselines
from decision_tree import decisionTree

def main():
    # List of commands
    print("Type one of the following numbers to execute the command: ")
    print("1. test baseline")
    print("2. test decision tree")
    print("3. baseline")
    print("4. decision tree")
    print("")

    userInput = input("> ")

    if userInput == '1':
        data = extract_data("dialog_acts.dat")
        testBaselines(data)
    elif userInput == '2':
        decisionTree('test')
    elif userInput == '3':
        classify_user_input()
    elif userInput == '4':
        decisionTree('')

def classify_user_input():
    data = extract_data("dialog_acts.dat")
    
    """
    Classifies input from the user into a certain dialog act group.  
    """
    
    sentence = (str(input('Enter sentence: '))).lower().split()
    
    if (len(sentence) > 0):
        print('Majority classification is: '  + majority_baseline(data)[0])
        print('Rule based classification is: '  + rule_based_baseline(sentence)[0])
