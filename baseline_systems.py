from extract import Extract

class BaseLineSystem:
    def __init__(self):
        self.data = Extract("data/dialog_acts.dat")

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
        classification = []
        check_data_type = isinstance(input, Extract)
        
        sentences_test = input.sentences_test if check_data_type else [input]
        
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
        mBaseline = self.majority_baseline(self.data)
        rbBaseline = self.rule_based_baseline(self.data)  

        i = 0
        rbCorrect = 0
        for output in rbBaseline: 
            if output == self.data.dialog_acts_test[i]: 
                rbCorrect += 1
            i += 1

        i = 0
        mCorrect = 0

        for output in mBaseline: 
            if output == self.data.dialog_acts_test[i]:
                mCorrect += 1
            i += 1

        print(str(round(rbCorrect/len(self.data.sentences_test),3)) + " accuracy on the rule-based baseline")
        print(str(round(mCorrect/len(self.data.sentences_test),3)) + " accuracy on the majority baseline")

    def classify_user_input(self):
        # Classifies input from the user into a certain dialog act group.  
        
        sentence = (str(input('Enter sentence: '))).lower().split()
        
        if (len(sentence) > 0):
            print('Majority classification is: '  + self.majority_baseline(self.data)[0])
            print('Rule based classification is: '  + self.rule_based_baseline(sentence)[0])
        