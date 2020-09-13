from sklearn import datasets
from sklearn import tree
from sklearn.tree import export_text
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import confusion_matrix
from extract import extract_data
import numpy as np

def decisionTree():
    # Parsed data from "dialog_acts.dat", with 85% training data
    extractData              = extract_data("dialog_acts.dat", 0.85)

    # Array of values from each data key
    dialog_acts_train = extractData["dialog_acts_train"]
    sentences_train   = extractData["sentences_train"]
    dialog_acts_test  = extractData["dialog_acts_test"]
    sentences_test    = extractData["sentences_test"]

    # Get maximum length of sentence
    max_len_train = len(max(sentences_train,key=len))
    max_len_test  = len(max(sentences_test,key=len))
    max_len       = max_len_test if max_len_test > max_len_train else max_len_train

    # Make all sentences equal in length to parse with OneHotEncoder to binary
    for sentence in sentences_train:
        for n in range(len(sentence), max_len, 1): sentence.insert(n, '')

    for sentence in sentences_test:
        for n in range(len(sentence), max_len, 1): sentence.insert(n, '')

    # Convert string lists to binary lists, since SciKit decision tree does not support string data        
    oneHotEncoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
    oneHotEncoder.fit(sentences_train)
    binarySentences = oneHotEncoder.transform(sentences_train)

    # Create the decision tree
    decisionTreeClassifier = tree.DecisionTreeClassifier()
    decisionTreeClassifier = decisionTreeClassifier.fit(binarySentences, dialog_acts_train)

    # Print decision tree
    # r = export_text(decisionTreeClassifier)
    # print(r)

    # Console writeline
    while True:
        print("Type message: ")
        choice = input("> ")

        # Write 'test' in console to start testing sequence
        if (choice == 'test'):
            matrix      = {}
            labels      = []
            predictions = []
            actually    = []
            tested      = 0
            correct     = 0

            for matrixAct in dialog_acts_train:
                if matrixAct not in matrix:
                    matrix[matrixAct] = {}
                    labels.append(matrixAct)
                    for matrixActSecond in dialog_acts_train:
                        if matrixActSecond not in matrix[matrixAct]: matrix[matrixAct][matrixActSecond] = 0

            for n in range(0, len(dialog_acts_test), 1):
                dialog = dialog_acts_test[n]
                sentence = sentences_test[n]

                prediction = oneHotEncoder.transform([sentence])
                answer = decisionTreeClassifier.predict(prediction)
                
                if (answer[0] == dialog): correct = correct + 1
                tested = tested + 1
                predictions.append(answer[0])
                actually.append(dialog)
                matrix[answer[0]][dialog] = matrix[answer[0]][dialog] + 1
            
            print(10*' ' + ' | '.join(matrix.keys()))
            for key, value in matrix.items():
                print("%-10s" % (key), end = '')
                print(*value.values(), sep = 7*' ' + "|")
            
            # print(confusion_matrix(actually, predictions, labels=labels))
            print("Total tested sentences: " + str(tested))
            print("Total correctly classified: " + str(correct))
            print("Finished testing, results: " + str(float(100 / tested * correct)) + "% correct")
        else:
            # Label user input
            choice = choice.lower().split(' ')

            if (len(choice) < max_len):
                for n in range(len(choice), max_len, 1): choice.insert(n, '')
            else:
                choice = choice[0:max_len]

            prediction = oneHotEncoder.transform([choice])
            answer     = decisionTreeClassifier.predict(prediction)

            print("Answer is: " + answer[0])

            # Quit program if the answer given is labeled 'bye'
            if answer[0] == 'bye': break

decisionTree()