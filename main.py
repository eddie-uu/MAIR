from baseline_systems import baseline_system
from decision_tree import decision_tree
from dialog_flow import dialog_flow
from mlp import multi_layer_perceptron
from extract import extract

def main():
    # List of commands
    commands = {
        '1': {'function': use_baseline,       'testing': True,  'description': 'Test baseline'},
        '2': {'function': use_decision_tree,  'testing': True,  'description': 'Test decision tree'},
        '3': {'function': use_mlp,            'testing': True,  'description': 'Test neural network'},
        '4': {'function': use_baseline,       'testing': False, 'description': 'Baseline'},
        '5': {'function': use_decision_tree,  'testing': False, 'description': 'Decision tree'},
        '6': {'function': use_mlp,            'testing': False, 'description': 'Neural network'},
        '7': {'function': use_dialog_flow,    'testing': False, 'description': 'Dialog'},
        '8': {'function': configure_settings, 'testing': False, 'description': 'Change settings'}
    }

    print("Type one of the following numbers to execute the command: ")
    for key in commands:
        print(key + '. ' + commands[key]['description'])

    userInput = input("> ")
    if userInput in commands.keys():
        command = commands[userInput]
        command['function'](command['testing'])

def use_baseline(testing = False):
    bls = baseline_system()
    bls.perform_algorithm(testing)

def use_decision_tree(testing = False):
    dt = decision_tree()
    dt.perform_algorithm(testing)

def use_mlp(testing = False):
    mlp = multi_layer_perceptron()
    mlp.perform_algorithm(testing)

def use_dialog_flow(testing = False):
    dialogFlow = dialog_flow()
    dialogFlow.Welcome()

def configure_settings(testing = False):
    settings = extract()
    settings.configure_settings()

main()