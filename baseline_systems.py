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
            {'key': 'confirm',  'value': ['serve', 'is', 'does']}, # or sentence[0] == 'is' or sentence[0] == 'does':
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

    def testBaselines(self):
        """
            Calculates the accuracy of both baseline classifications and prints them to the console.
            Accuracy is calculated by taking the number of correct classifications and dividing it by the total number of classifications.
        """ 
        mBaseline  = self.majority_baseline(self.extractData)
        rbBaseline = self.rule_based_baseline(self.extractData)  
        mMatrix    = {}
        rbMatrix   = {}
        mTested    = 0
        rbTested   = 0
        mCorrect   = 0
        rbCorrect  = 0

        self.extractData.dialog_acts_train.append('total')

        for matrixAct in self.extractData.dialog_acts_train:
            if matrixAct not in rbMatrix:
                rbMatrix[matrixAct] = {}
                mMatrix[matrixAct] = {}
                for matrixActSecond in self.extractData.dialog_acts_train:
                    if matrixActSecond not in rbMatrix[matrixAct]:
                        rbMatrix[matrixAct][matrixActSecond] = 0
                        mMatrix[matrixAct][matrixActSecond] = 0
        
        for output in rbBaseline:
            dialog = self.extractData.dialog_acts_test[rbTested]
            answer = output
            if dialog == answer:
                rbCorrect += 1
            
            rbMatrix[answer][dialog] = rbMatrix[answer][dialog] + 1
            rbMatrix[answer]['total'] = rbMatrix[answer]['total'] + 1
            rbMatrix['total'][dialog] = rbMatrix['total'][dialog] + 1
            rbTested += 1

        for output in mBaseline: 
            dialog = self.extractData.dialog_acts_test[mTested]
            answer = output
            if dialog == answer:
                mCorrect += 1
            
            mMatrix[answer][dialog] = mMatrix[answer][dialog] + 1
            mMatrix[answer]['total'] = mMatrix[answer]['total'] + 1
            mMatrix['total'][dialog] = mMatrix['total'][dialog] + 1
            mTested += 1

        
        for key, value in rbMatrix.items():
            if key != 'total':
                print("Precision for " + key + ": " + str(value[key] / value['total']))
                print("Recall for " + key + ": " + str(value[key] / rbMatrix['total'][key]))

        # for key, value in mMatrix.items():
        #    if key != 'total':
        #        print(str(value['total']))
        #        print("Precision for " + key + ": " + str(value[key] / value['total']))
        #        print("Recall for " + key + ": " + str(value[key] / mMatrix['total'][key]))


        print(str(round(rbCorrect/rbTested,3)) + " accuracy on the rule-based baseline")
        print(str(round(mCorrect/mTested,3)) + " accuracy on the majority baseline")

    def classify_user_input(self):
        # Classifies input from the user into a certain dialog act group.  
        
        sentence = (str(input('Enter sentence: '))).lower().split()
        
        if (len(sentence) > 0):
            print('Majority classification is: '  + self.majority_baseline(self.extractData)[0])
            print('Rule based classification is: '  + self.rule_based_baseline(sentence)[0])
        