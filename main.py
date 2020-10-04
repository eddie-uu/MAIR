from baseline_systems import baseline_system
from decision_tree import decision_tree
from dialog_flow import dialog_flow
from mlp import multi_layer_perceptron

def main():
    commands = {
        '1': {'function': useBaseLine, 'testing': True, 'description': 'Test baseline'},
        '2': {'function': useDecisionTree, 'testing': True, 'description': 'Test decision tree'},
        '3': {'function': useMLP, 'testing': True, 'description': 'Test neural network'},
        '4': {'function': useBaseLine, 'testing': False, 'description': 'Baseline'},
        '5': {'function': useDecisionTree, 'testing': False, 'description': 'Decision tree'},
        '6': {'function': useMLP, 'testing': False, 'description': 'Neural network'},
        '7': {'function': useDialogFlow, 'testing': False, 'description': 'Dialog'}
    }

    # List of commands
    print("Type one of the following numbers to execute the command: ")
    for key in commands:
        print(key + '. ' + commands[key]['description'])

    userInput = input("> ")
    if userInput in commands.keys():
        command = commands[userInput]
        command['function'](command['testing'])

def useBaseLine(testing = False):
    bls = baseline_system()
    bls.perform_algorithm(testing)

def useDecisionTree(testing = False):
    dt = decision_tree()
    dt.perform_algorithm(testing)

def useMLP(testing = False):
    mlp = multi_layer_perceptron()
    mlp.perform_algorithm(testing)

def useDialogFlow(testing = False):
    dialogFlow = dialog_flow()
    dialogFlow.welcome()

main()