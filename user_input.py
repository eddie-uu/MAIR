from baseline_systems import majority_baseline
from baseline_systems import rule_based_baseline

def classify_user_input():
    
    """
    Classifies input from the user into a certain dialog act group.  
    """
    
    sentence = (str(input('Enter sentence: '))).lower().split()
    
    print('Majority classification is: '  + majority_baseline(data)[0])
    print('Rule based classification is: '  + rule_based_baseline(sentence)[0])