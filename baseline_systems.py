import random

with open('dialog_acts.dat') as f:
    data = f.readlines()

data = [sentence[:-1] for sentence in data]

# random.shuffle(data)

train_size = round(len(data) * 0.85)
training = data[:train_size]
test = data[train_size:]

dialog_acts_train = [sentence.split(' ')[0] for sentence in training]
sentences_train = [sentence.split(' ')[1:] for sentence in training]
dialog_acts_test = [sentence.split(' ')[0] for sentence in test]
sentences_test = [sentence.split(' ')[1:] for sentence in test]


def majority_baseline():
    counts = dict()
        
    for act in dialog_acts_train:
        if act in counts:
            counts[act] += 1
        else:
            counts[act] = 1
            
        if counts[act] == max(counts.values()):
            most_common_act = act
            
    classification = []
    
    for sentence in sentences_test:
        classification.append(most_common_act)
        
    return classification


def rule_based_baseline():
    classification = []
    
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
    
#classification = []
klas = rule_based_baseline()
    
    
    
    
    