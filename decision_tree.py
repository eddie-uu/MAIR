from sklearn import datasets
from sklearn import tree
from sklearn.tree import export_text
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from extract import extract_data
import numpy as np

def decisionTree():
    # Parsed data from "dialog_acts.dat", with 85% training data
    data              = extract_data("dialog_acts.dat", 0.85)

    # Array of values from each data key
    dialog_acts_train = data["dialog_acts_train"]
    sentences_train   = data["sentences_train"]
    dialog_acts_test  = data["dialog_acts_test"]
    sentences_test    = data["sentences_test"]

    # Get maximum length of sentence
    max_len_train = len(max(sentences_train,key=len))
    max_len_test = len(max(sentences_test,key=len))
    max_len = max_len_train

    if (max_len_test > max_len_train):
        max_len = max_len_test

    # Make all sentences equal in length to parse with OneHotEncoder to binary
    for sentence in sentences_train:
        for n in range(len(sentence), max_len, 1):
            sentence.insert(n, '')

    for sentence in sentences_test:
        for n in range(len(sentence), max_len, 1):
            sentence.insert(n, '')

    # Convert string lists to binary lists, since SciKit decision tree does not support string data        
    oneHotEncoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
    oneHotEncoder.fit(sentences_train)
    oneHotLabels = oneHotEncoder.transform(sentences_train)

    # Create the decision tree
    decisionTreeClassifier = tree.DecisionTreeClassifier()
    decisionTreeClassifier = decisionTreeClassifier.fit(oneHotLabels, dialog_acts_train)

    # Print decision tree
    # r = export_text(decisionTreeClassifier)
    # print(r)

    # Console writeline
    while True:
        print("Message: ")
        choice = input("> ")
        
        # Write 'test' in console to start testing sequence
        if (choice == 'test'):
            tested = 0
            correct = 0
            for n in range(0, len(dialog_acts_test), 1):
                dialog = dialog_acts_test[n]
                sentence = sentences_test[n]

                prediction = oneHotEncoder.transform([sentence])
                answer = decisionTreeClassifier.predict(prediction)
                
                if (answer[0] == dialog):
                    correct = correct + 1
                tested = tested + 1    
            
            print("Tested sentences: " + str(tested))
            print("Correctly classified: " + str(correct))
            print("Finished testing, results: " + str(float(100 / tested * correct)) + "% correct")
            break
        else:
            # Label user input
            choice = choice.lower().split(' ')

            if (len(choice) < max_len):
                for n in range(len(choice), max_len, 1):
                    choice.insert(n, '')
            else:
                choice = choice[0:max_len]

            prediction = oneHotEncoder.transform([choice])
            answer = decisionTreeClassifier.predict(prediction)

            print(answer)

            # Quit program if the answer given is labeled 'bye'
            if answer[0] == 'bye':
                break

decisionTree()