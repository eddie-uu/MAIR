from extract import Extract

class BaseLineSystem:
    def __init__(self):
        self.extractData = Extract("data/dialog_acts.dat")

    def majority_baseline(self, input):
        """
            Returns a classification (list) that labels every utterance with the most common dialog act, given a dataset.
            The index of a value in the classification list corresponds with the same index in the testset.
            @param input: should consist of the following keys: 
                - 'dialog_acts_train'
                - 'sentences_train'
                - 'dialog_acts_test'
                - 'sentences_test'
        """
        counts = dict()
            
        for act in input.dialog_acts_train:
            counts[act] = counts[act] + 1 if act in counts else 1
            
            if counts[act] == max(counts.values()):
                most_common_act = act
                
        classification = []
        
        for sentence in input.sentences_test:
            classification.append(most_common_act)
            
        return classification

    def rule_based_baseline(self, input):
        """
            Returns a classification that labels every utterance based on a pre-defined ruleset, given a dataset.

            The ruleset is constructed by checking the data and seeing which terms are often associated with which dialog acts. If that term is in the sentence, 
            we give it the corresponding dialog act classification. If no matching term is found, we default to the "inform" dialog act.

            The higher dialog acts in our if-...-else construction are expected to be more determining than the lower dialog acts 
            (e.g. the word "thank" takes priority over the word 'other').

            The index of a value in the classification list corresponds with the same index in the testset.

            @param input: should consist of the same keys as in majority_baseline()
        """
        classification  = []
        check_data_type = isinstance(input, Extract)
        sentences_test  = input.sentences_test if check_data_type else [input]
        
        sentence_types = [
            {'key': 'thankyou', 'value': ['thank', 'thanks', 'appreciate', 'grateful']},
            {'key': 'bye',      'value': ['goodbye', 'bye']},
            {'key': 'reqalts',  'value': ['other', 'another', 'anything', 'else']},
            {'key': 'hello',    'value': ['hi', 'hello', 'hey']},
            {'key': 'affirm',   'value': ['yes', 'right', 'correct', 'exactly']},
            {'key': 'ack',      'value': ['okay']},
            {'key': 'deny',     'value': ['wrong', 'not']},
            {'key': 'reqmore',  'value': ['more', 'additional']},
            {'key': 'negate',   'value': ['no']},
            {'key': 'inform',   'value': ['dont', 'cheap', 'part', 'vegetarian', 'matter']},
            {'key': 'repeat',   'value': ['again', 'repeat', 'back']},
            {'key': 'restart',  'value': ['start', 'over', 'reset', 'restart']},
            {'key': 'request',  'value': ['address', 'phone', 'number']},
            {'key': 'confirm',  'value': ['serve', 'is', 'does']},
            {'key': 'null',     'value': ['wait', 'unintelligible', 'noise', 'cough', 'sorry', 'sil', 'knocking', 'um', 'laughing']}
        ]

        for sentence in sentences_test:
            added = False
            for types in sentence_types:
                if any(x in types['value'] for x in sentence):
                    classification.append(types['key'])
                    added = True
                    break

            if not added:
                classification.append('inform')

        return classification

    def performAlgorithm(self, decisionType = False):
        if decisionType:
            """
                Calculates the accuracy of both baseline classifications and prints them to the console.
                Accuracy is calculated by taking the number of correct classifications and dividing it by the total number of classifications.
            """ 
            mBaseline  = self.majority_baseline(self.extractData)
            rbBaseline = self.rule_based_baseline(self.extractData)  
            mMatrix    = {}
            rbMatrix   = {}

            self.extractData.dialog_acts_train.append('total')

            for matrixAct in self.extractData.dialog_acts_train:
                if matrixAct not in rbMatrix:
                    rbMatrix[matrixAct] = {}
                    mMatrix[matrixAct] = {}
                    for matrixActSecond in self.extractData.dialog_acts_train:
                        if matrixActSecond not in rbMatrix[matrixAct]:
                            rbMatrix[matrixAct][matrixActSecond] = 0
                            mMatrix[matrixAct][matrixActSecond] = 0
            
            self.evaluateResults("rule-based", rbBaseline, rbMatrix)
            print("")
            self.evaluateResults("majority", mBaseline, mMatrix)
        else:
            # Classifies input from the user into a certain dialog act group.  
            
            sentence = (str(input('Enter sentence: '))).lower().split()
            
            if (len(sentence) > 0):
                print('Majority classification is: '  + self.majority_baseline(self.extractData)[0])
                print('Rule based classification is: '  + self.rule_based_baseline(sentence)[0])

    def evaluateResults(self, baselineType, baseline, matrix):
        tested = 0
        correct = 0
        for output in baseline: 
            dialog = self.extractData.dialog_acts_test[tested]
            answer = output
            if dialog == answer:
                correct += 1
            
            matrix[answer][dialog] = matrix[answer][dialog] + 1
            matrix[answer]['total'] = matrix[answer]['total'] + 1
            matrix['total'][dialog] = matrix['total'][dialog] + 1
            tested += 1

        print("Results on the " + baselineType + " baseline:")
        print(10*' ' + ' | '.join(matrix.keys()))
        for key, value in matrix.items():
            print("%-10s" % (key), end = '')
            print(*value.values(), sep = 7*' ' + "|")

        print(str((round(correct/tested,3) * 100)) + "% accuracy on the " + baselineType + " baseline")
        print("Individual values for labels: ")
        for key, value in matrix.items():
            if key != 'total':
                precision = 0 if value['total'] == 0 else value[key] / value['total']
                recall    = 0 if matrix['total'][key] == 0 else value[key] / matrix['total'][key]
                f1        = 0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)
                print("Precision for " + key + ": " + str(round(precision, 3)))
                print("Recall for " + key + ": " + str(round(recall, 3)))
                print("F1-measure for " + key + ": " + str(round(f1, 3)))
        