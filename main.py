from baseline_systems import BaseLineSystem
from decision_tree import DecisionTree
from dialog_flow import DialogFlow
from mlp import mlp_loop, mlp

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
    baseLineSystem = BaseLineSystem()
    baseLineSystem.testBaselines() if testing else baseLineSystem.classify_user_input()


def useDecisionTree(testing = False):
    dt = DecisionTree()
    dt.performDecisionTree('test') if testing else dt.performDecisionTree('')

def useMLP(testing = False):
    mlp("data/dialog_acts.dat") if testing else mlp_loop()

def useDialogFlow(testing = False):
    dialogFlow = DialogFlow()
    dialogFlow.Welcome()

main()