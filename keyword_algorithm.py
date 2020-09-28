import re

class KeywordAlgorithm:
    def __init(self):
        pass

    # Checks regex patterns (matching keywords) in sentence and returns either the sentence back if not found or the keyword match
    def checkPattern(self, text, patterns, defaultValue = ''):
        for pattern in patterns:
            match = re.search(pattern['pattern'], text)
            if match:
                text = match.group(pattern['group']) if defaultValue == '' else defaultValue 
        return text

    # Perform the algorithm for a sentence, pass a search mode (food, area or pricerange) if context is mentioned
    def keywordAlgorithm(self, text, mode = ''):
        response = {}
        text = text.lower()

        # General patterns for any option
        baseDontCarePatterns = [{'pattern': 'doesnt matter'}, {'pattern': 'dont care'}, {'pattern': 'any'}]
        
        # Checks whether the given sentence has a pricerange mentioned
        if mode == 'pricerange' or mode == '':
            # Price patterns / matching keywords
            pricePatterns = [{'pattern': '(cheap|moderately|expensive)', 'group': 1},
                            {'pattern': '(.+?) (priced)', 'group': 1}]                 
            
            # Add additional dontcare pattern specific to prices
            priceDontCarePatterns = baseDontCarePatterns
            priceDontCarePatterns.append({'pattern': 'any price'})
            
            # Check the given sentence
            result    = self.checkPattern(text, pricePatterns)
            result    = result.split()[-1] if len(result.split()) > 1 and result != text else result
            endResult = self.checkPattern(result, priceDontCarePatterns, 'dontcare')
            
            # If the given answer is invalid and the context is specific for pricerange, return dontcare
            if len(endResult.split()) > 1 and mode == 'pricerange':
                endResult = 'dontcare'

            # Add price range to response
            if len(endResult.split()) < 2 and endResult != '':
                text = text if endResult == 'dontcare' else text.replace(result, '')
                text = text.replace(' priced ', '')
                response['pricerange'] = endResult

        # Same functionality as pricerange, but for area
        if mode == 'area' or mode == '':
            areaPatterns = [{'pattern': '(center|centre)', 'group': 1},
                            {'pattern': '(north|south|east|west)', 'group': 1},
                            {'pattern': '(in the) (.*)', 'group': 2}]
            areaDontCarePatterns = baseDontCarePatterns
            areaDontCarePatterns.append({'pattern': 'any area'})
            areaDontCarePatterns.append({'pattern': 'any part'})

            result    = self.checkPattern(text, areaPatterns)
            result    = result.split()[-1] if len(result.split()) > 1 and result != text else result
            endResult = self.checkPattern(result, areaDontCarePatterns, 'dontcare')

            if len(endResult.split()) > 1 and mode == 'area':
                endResult = 'dontcare'

            if len(endResult.split()) < 2 and endResult != '':
                text = text if endResult == 'dontcare' else text.replace(result, '')
                response['area'] = endResult

        # Same functionality as pricerange, but for food
        if mode == 'food' or mode == '':
            foodPatterns = [{'pattern': '(.+?) (food)', 'group': 1},
                            {'pattern': '(serving|serves|serve) (.*)', 'group': 2},
                            {'pattern': '(with|about) (.*)', 'group': 2},
                            {'pattern': '(for|a) (.*)', 'group': 2},
                            {'pattern': '(.+?) (restaurant)', 'group': 1}]
            foodDontCarePatterns = baseDontCarePatterns
            foodDontCarePatterns.append({'pattern': 'any type'})

            result    = self.checkPattern(text, foodPatterns)
            endResult = self.checkPattern(result, foodDontCarePatterns, 'dontcare')
            
            foodType = True
            for words in endResult.split():
                if len(words) < 3: foodType = False

            if not foodType and mode == 'food':
                endResult = 'dontcare'
                foodType = True

            if foodType and endResult != '': response['food'] = endResult
        
        return response