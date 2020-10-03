import re

class keyword_algorithm:
    def __init(self):
        pass

    # Checks regex patterns (matching keywords) in sentence and returns either the sentence back if not found or the keyword match
    def checkPattern(self, text, patterns, default_value = ''):
        for pattern in patterns:
            match = re.search(pattern['pattern'], text)
            if match:
                text = match.group(pattern['group']) if default_value == '' else default_value 
        return text

    # Perform the algorithm for a sentence, pass a search mode (food, area or pricerange) if context is mentioned
    def keyword_algorithm(self, text, mode = ''):
        response = {}
        sentences = text.split('and')

        for sentence in sentences:
            self.perform_algorithm(sentence, mode, response)
        
        return response

    def perform_algorithm(self, text, mode, response):
        text = text.lower()

        # General patterns for any option
        base_dont_care_patterns = [{'pattern': 'doesnt matter'}, {'pattern': 'dont care'}, {'pattern': 'any'}]
        
        # Checks whether the given sentence has a pricerange mentioned
        if mode == 'pricerange' or mode == '':
            # Price patterns / matching keywords
            price_patterns = [{'pattern': '(cheap|moderately|expensive)', 'group': 1},
                            {'pattern': '(.+?) (priced)', 'group': 1}]                 
            
            # Add additional dontcare pattern specific to prices
            price_dont_care_patterns = base_dont_care_patterns
            price_dont_care_patterns.append({'pattern': 'any price'})
            
            # Check the given sentence
            result    = self.checkPattern(text, price_patterns)
            result    = result.split()[-1] if len(result.split()) > 1 and result != text else result
            end_result = self.checkPattern(result, price_dont_care_patterns, 'dontcare')
            
            # If the given answer is invalid and the context is specific for pricerange, return dontcare
            if len(end_result.split()) > 1 and mode == 'pricerange':
                end_result = 'dontcare'

            # Add price range to response
            if len(end_result.split()) < 2 and end_result != '':
                text = text if end_result == 'dontcare' else text.replace(result, '')
                text = text.replace(' priced ', '')
                response['pricerange'] = end_result

        # Same functionality as pricerange, but for area
        if mode == 'area' or mode == '':
            area_patterns = [{'pattern': '(center|centre)', 'group': 1},
                            {'pattern': '(north|south|east|west)', 'group': 1},
                            {'pattern': '(in the) (.*)', 'group': 2}]
            area_dont_care_patterns = base_dont_care_patterns
            area_dont_care_patterns.append({'pattern': 'any area'})
            area_dont_care_patterns.append({'pattern': 'any part'})

            result    = self.checkPattern(text, area_patterns)
            result    = result.split()[-1] if len(result.split()) > 1 and result != text else result
            end_result = self.checkPattern(result, area_dont_care_patterns, 'dontcare')

            if len(end_result.split()) > 1 and mode == 'area':
                end_result = 'dontcare'

            if len(end_result.split()) < 2 and end_result != '':
                text = text if end_result == 'dontcare' else text.replace(result, '')
                response['area'] = end_result

        # Same functionality as pricerange, but for food
        if mode == 'food' or mode == '':
            food_patterns = [{'pattern': '(.+?) (food)', 'group': 1},
                            {'pattern': '(serving|serves|serve) (.*)', 'group': 2},
                            {'pattern': '(with|about) (.*)', 'group': 2},
                            {'pattern': '(for|a) (.*)', 'group': 2},
                            {'pattern': '(.+?) (restaurant)', 'group': 1}]
            food_dont_care_patterns = base_dont_care_patterns
            food_dont_care_patterns.append({'pattern': 'any type'})

            result    = self.checkPattern(text, food_patterns)
            end_result = self.checkPattern(result, food_dont_care_patterns, 'dontcare')
            
            food_type = True
            for words in end_result.split():
                if len(words) < 3: food_type = False

            if not food_type and mode == 'food':
                end_result = 'dontcare'
                food_type  = True

            if food_type and end_result != '':
                response['food'] = end_result
        
        return response