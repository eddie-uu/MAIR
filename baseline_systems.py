from extract import Extract

class BaseLineSystem:
    def __init(self):
        pass

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
            if act in counts:
                counts[act] += 1
            else:
                counts[act] = 1
                
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
        
        if check_data_type:
            sentences_test = input.sentences_test
        else:
            sentences_test = [input]
            
        for sentence in sentences_test:
            if any(x in ['thank', 'thanks', 'appreciate', 'grateful'] for x in sentence):
                classification.append('thankyou')
            elif any(x in ['goodbye', 'bye'] for x in sentence):
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
            elif any(x in ['again', 'repeat', 'back'] for x in sentence):
                classification.append('repeat')
            elif any(x in ['start', 'over', 'reset', 'restart'] for x in sentence):
                classification.append('restart')
            elif any(x in ['address', 'phone', 'number'] for x in sentence):
                classification.append('request')
            elif any(x in ['serve'] for x in sentence) or sentence[0] == 'is' or sentence[0] == 'does':
                classification.append('confirm')
            elif any(x in ['wait', 'unintelligible', 'noise', 'cough', 'sorry', 'sil', 'knocking', 'um', 'laughing'] for x in sentence):
                classification.append('null')
            else:
                classification.append('inform')
                
        return classification

    def testBaselines(self, input):
        data = Extract("data/dialog_acts.dat")
        """
            Calculates the accuracy of both baseline classifications and prints them to the console.
            Accuracy is calculated by taking the number of correct classifications and dividing it by the total number of classifications.
        """ 
        mBaseline = self.majority_baseline(input)
        rbBaseline = self.rule_based_baseline(input)  
        i = 0
        rbCorrect = 0
        for output in rbBaseline: 
            if output == data.dialog_acts_test[i]: 
                rbCorrect += 1
            i += 1
        print(str(round(rbCorrect/len(data.sentences_test),3)) + " accuracy on the rule-based baseline")
        i = 0
        mCorrect = 0
        for output in mBaseline: 
            if output == data.dialog_acts_test[i]:
                mCorrect += 1
            i += 1
        print(str(round(mCorrect/len(data.sentences_test),3)) + " accuracy on the majority baseline")
        