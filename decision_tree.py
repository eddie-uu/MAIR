from abstract_mla import AbstractMachineLearningAlgorithm
from sklearn import datasets
from sklearn import tree
from sklearn.tree import export_text
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.metrics import confusion_matrix
from extract import Extract
import numpy as np
import pickle
import os

class DecisionTree(AbstractMachineLearningAlgorithm):
    def __init__(self):
        print('Creating decision tree...')
        # Parsed data from "dialog_acts.dat", with 85% training data
        extractData = Extract("data/dialog_acts.dat")

        # Array of values from each data key
        sentences_train   = extractData.sentences_train
        sentences_test    = extractData.sentences_test

        # Get maximum length of sentence
        max_len_train = len(max(sentences_train,key=len))
        max_len_test  = len(max(sentences_test,key=len))
        max_len       = max_len_test if max_len_test > max_len_train else max_len_train

        filename               = 'data/decision_tree.pkl'
        decisionTreeClassifier = None

        # Make all sentences equal in length to parse with OneHotEncoder to binary
        for sentence in sentences_train:
            for n in range(len(sentence), max_len, 1): sentence.insert(n, '')

        for sentence in sentences_test:
            for n in range(len(sentence), max_len, 1): sentence.insert(n, '')

        # Convert string lists to binary lists, since SciKit decision tree does not support string data        
        oneHotEncoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
        oneHotEncoder.fit(sentences_train)
        
        if os.path.exists(filename):
            decisionTreeClassifier = pickle.load(open(filename, 'rb'))
        else:
            # Create the decision tree
            binarySentences = oneHotEncoder.transform(sentences_train)
            decisionTreeClassifier = tree.DecisionTreeClassifier()
            decisionTreeClassifier = decisionTreeClassifier.fit(binarySentences, extractData.dialog_acts_train)

            pickle.dump(decisionTreeClassifier, open(filename, 'wb'))

        self.oneHotEncoder = oneHotEncoder
        self.decisionTree  = decisionTreeClassifier
        self.max_len       = max_len
        self.extractData   = extractData

    def predict(self, choice):
        # Label user input
        choice = choice.lower().split(' ')

        if (len(choice) < self.max_len):
            for n in range(len(choice), self.max_len, 1): choice.insert(n, '')
        else:
            choice = choice[0:self.max_len]

        prediction = self.oneHotEncoder.transform([choice])
        answer     = self.decisionTree.predict(prediction)

        return answer[0]

    # overriding abstract method
    def performAlgorithm(self, decisionType = False):
        # Make all sentences equal in length to parse with OneHotEncoder to binary
        for sentence in self.extractData.sentences_train:
            for n in range(len(sentence), self.max_len, 1): sentence.insert(n, '')

        for sentence in self.extractData.sentences_test:
            for n in range(len(sentence), self.max_len, 1): sentence.insert(n, '')
  
        # Write 'test' in console to start testing sequence
        if decisionType:
            matrix  = {}
            tested  = 0
            correct = 0

            self.extractData.dialog_acts_train.append('total')

            for matrixAct in self.extractData.dialog_acts_train:
                if matrixAct not in matrix:
                    matrix[matrixAct] = {}
                    for matrixActSecond in self.extractData.dialog_acts_train:
                        if matrixActSecond not in matrix[matrixAct]:
                            matrix[matrixAct][matrixActSecond] = 0

            f = open("data/wrong answers.txt", "w")
            for n in range(0, len(self.extractData.dialog_acts_test), 1):
                dialog     = self.extractData.dialog_acts_test[n]
                sentence   = self.extractData.sentences_test[n]
                prediction = self.oneHotEncoder.transform([sentence])
                answer     = self.decisionTree.predict(prediction)
                tested     = tested + 1
                        
                if (answer[0] == dialog):
                    correct = correct + 1
                else:
                    s = ' '.join(sentence)
                    f.write(s + " -- Predicted: " + answer[0] + " -- Actually: " + dialog + "\n")

                matrix[answer[0]][dialog] = matrix[answer[0]][dialog] + 1
                matrix[answer[0]]['total'] = matrix[answer[0]]['total'] + 1
                matrix['total'][dialog] = matrix['total'][dialog] + 1

            f.close()
            print(10*' ' + ' | '.join(matrix.keys()))
            for key, value in matrix.items():
                print("%-10s" % (key), end = '')
                print(*value.values(), sep = 7*' ' + "|")
            
            for key, value in matrix.items():
                if key != 'total':
                    precision = 0 if value['total'] == 0 else value[key] / value['total']
                    recall    = 0 if matrix['total'][key] == 0 else value[key] / matrix['total'][key]
                    f1        = 0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)
                    print("Precision for " + key + ": " + str(round(precision, 3)))
                    print("Recall for " + key + ": " + str(round(recall, 3)))
                    print("F1-measure for " + key + ": " + str(round(f1, 3)))

            print("")
            print("Total tested sentences: " + str(tested))
            print("Total correctly classified: " + str(correct))
            print("Accuracy: " + str(round(100 / tested * correct, 3)) + "%")
        else:
            # Console writeline
            while True:
                print("Type message: ")
                choice = input("> ")

                # Label user input
                choice = choice.lower().split(' ')

                if (len(choice) < self.max_len):
                    for n in range(len(choice), self.max_len, 1): choice.insert(n, '')
                else:
                    choice = choice[0:self.max_len]

                prediction = self.oneHotEncoder.transform([choice])
                answer     = self.decisionTree.predict(prediction)

                print("Answer is: " + answer[0])

                # Quit program if the answer given is labeled 'bye'
                if answer[0] == 'bye': break