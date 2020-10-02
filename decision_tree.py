from sklearn import datasets
from sklearn import tree
from sklearn.tree import export_text
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.metrics import confusion_matrix
from extract import Extract
import numpy as np

class DecisionTree:
    def __init__(self):
        print('Creating decision tree...')
        # Parsed data from "dialog_acts.dat", with 85% training data
        extractData = Extract("data/dialog_acts.dat")

        # Array of values from each data key
        dialog_acts_train = extractData.dialog_acts_train
        sentences_train   = extractData.sentences_train
        sentences_test    = extractData.sentences_test

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

        self.oneHotEncoder = oneHotEncoder
        self.decisionTree = decisionTreeClassifier
        self.max_len = max_len
        self.extractData = extractData

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

    def performDecisionTree(self, decisionType):
        # Make all sentences equal in length to parse with OneHotEncoder to binary
        for sentence in self.extractData.sentences_train:
            for n in range(len(sentence), self.max_len, 1): sentence.insert(n, '')

        for sentence in self.extractData.sentences_test:
            for n in range(len(sentence), self.max_len, 1): sentence.insert(n, '')
  
        # Write 'test' in console to start testing sequence
        if (decisionType == 'test'):
            matrix      = {}
            labels      = []
            predictions = []
            actually    = []
            tested      = 0
            correct     = 0

            self.extractData.dialog_acts_train.append('total')

            for matrixAct in self.extractData.dialog_acts_train:
                if matrixAct not in matrix:
                    matrix[matrixAct] = {}
                    labels.append(matrixAct)
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
                    
                predictions.append(answer[0])
                actually.append(dialog)
                matrix[answer[0]][dialog] = matrix[answer[0]][dialog] + 1
                matrix[answer[0]]['total'] = matrix[answer[0]]['total'] + 1
                matrix['total'][dialog] = matrix['total'][dialog] + 1

            f.close()
            print(10*' ' + ' | '.join(matrix.keys()))
            for key, value in matrix.items():
                print("%-10s" % (key), end = '')
                print(*value.values(), sep = 7*' ' + "|")
            
            totalTrue = 0
            totalPrecisionPredicted = 0
            totalRecallPredicted = 0

            for key, value in matrix.items():
                if key != 'total':
                    totalTrue += value[key]
                    totalPrecisionPredicted += value['total']
                    totalRecallPredicted += matrix['total'][key]
                    print("Precision for " + key + ": " + str(value[key] / value['total']))
                    print("Recall for " + key + ": " + str(value[key] / matrix['total'][key]))

            print("")
            print("Total tested sentences: " + str(tested))
            print("Total correctly classified: " + str(correct))
            print("Finished testing")
            print("Accuracy: " + str(float(100 / tested * correct)) + "%")
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