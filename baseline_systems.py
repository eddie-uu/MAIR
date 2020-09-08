from extract import extract_data

data = extract_data("dialog_acts.dat")

def majority_baseline():
    counts = dict()
        
    for act in data['dialog_acts_train']:
        if act in counts:
            counts[act] += 1
        else:
            counts[act] = 1
            
        if counts[act] == max(counts.values()):
            most_common_act = act
            
    classification = []
    
    for sentence in data['sentences_test']:
        classification.append(most_common_act)
        
    return classification


def rule_based_baseline():
    classification = []
    sentences_test = data['sentences_test']
    for sentence in sentences_test:
        if any(x in ['thank', 'thanks', 'appreciate', 'grateful'] for x in sentence):
            classification.append('thankyou')
        elif 'goodbye'in sentence:
            classification.append('bye')
        elif any(x in ['other', 'another', 'anything', 'else'] for x in sentence):
            classification.append('reqalts')
        elif any(x in ['hi', 'hello', 'hey'] for x in sentence):
            classification.append('hello')
        elif any(x in ['yes', 'right', 'correct', 'exactly'] for x in sentence):
            classification.append('affirm')
        elif any(x in ['okay'] for x in sentence):
            classification.append('ack')
        elif any(x in ['wrong', 'not'] for x in sentence):
            classification.append('deny')
        elif any(x in ['more', 'additional'] for x in sentence):
            classification.append('reqmore')
        elif any(x in ['no'] for x in sentence):
            classification.append('negate')
        elif any(x in ['dont', 'cheap', 'part', 'vegetarian', 'matter'] for x in sentence):
            classification.append('inform')
        elif any(x in ['again', 'reoeat', 'back'] for x in sentence):
            classification.append('repeat')
        elif any(x in ['start', 'over', 'reset', 'restart'] for x in sentence):
            classification.append('restart')
        elif any(x in ['address', 'phone', 'number'] for x in sentence):
            classification.append('request')
        elif any(x in ['serve'] for x in sentence) or sentence[0] == 'is' or sentence[0] == 'does':
            classification.append('confirm')
        elif any(x in ['wait', 'unintelligible', 'noise', 'cough', 'sorry', 'sill', 'knocking', 'um', 'laughing'] for x in sentence):
            classification.append('null')
        else:
            classification.append('inform')
            
    return classification

def testBaselines():
    mBaseline = majority_baseline()
    rbBaseline = rule_based_baseline()  
    i = 0
    rbCorrect = 0
    for output in rbBaseline: 
        if output == data['dialog_acts_test'][i]:
            rbCorrect += 1
        i += 1
    print(str(round(rbCorrect/len(data['sentences_test']),3)) + " accuracy on the rule-based baseline")
    i = 0
    mCorrect = 0
    for output in mBaseline: 
        if output == data['dialog_acts_test'][i]:
            mCorrect += 1
        i += 1
    print(str(round(mCorrect/len(data['sentences_test']),3)) + " accuracy on the majority baseline")

if input("Baseline systems generated. Type 'test' to test.") == 'test':
    testBaselines()    
    
    