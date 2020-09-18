import re
def checkPattern(text, patterns, defaultValue = ''):
    for pattern in patterns:
        match = re.search(pattern['pattern'], text)
        if match:
            text = match.group(pattern['group']) if defaultValue == '' else defaultValue 
    return text

def keywordAlgorithm(text, mode):
    text = text.lower()
    dontCarePatterns = [{'pattern': 'any'}, {'pattern': 'doesnt matter'}, {'pattern': 'dont care'}]
    
    if mode == 'food':
        foodPatterns = [{'pattern': '(.+?) (food)', 'group': 1},
                        {'pattern': '(serving|serves|serve) (.*)', 'group': 2},
                        {'pattern': '(with|about) (.*)', 'group': 2},
                        {'pattern': '(for|a) (.*)', 'group': 2},
                        {'pattern': '(.+?) (restaurant)', 'group': 1}]

        text = checkPattern(text, foodPatterns)
        text = checkPattern(text, dontCarePatterns, 'dontcare')
        return text

    elif mode == 'price':
        pricePatterns = [{'pattern': '(cheap)', 'group': 1},
                         {'pattern': '(moderately)', 'group': 1},
                         {'pattern':'(expensive)', 'group': 1}]
        
        text = checkPattern(text, pricePatterns)
        text = checkPattern(text, dontCarePatterns, 'dontcare')
        return text
    elif mode == 'location':
        areaPatterns = [{'pattern': '(center)', 'group': 1},
                        {'pattern': '(north)', 'group': 1},
                        {'pattern': '(south)', 'group': 1},
                        {'pattern': '(east)', 'group': 1},
                        {'pattern': '(west)', 'group': 1}]

        text = checkPattern(text, areaPatterns)
        text = checkPattern(text, dontCarePatterns, 'dontcare')
        return text

texts = ['I\'m looking for world food',
         'I want a restaurant that serves world food',
         'I want a restaurant serving Swedish food',
         'I\'m looking for a restaurant in the center',
         'I would like a cheap restaurant in the west part of town',
         'I\'m looking for a moderately priced restaurant in the west part of town',
         'I\'m looking for a restaurant in any area that serves Tuscan food',
         'Can I have an expensive restaurant',
         'I\'m looking for an expensive restaurant and it should serve international food',
         'I need a Cuban restaurant that is moderately priced',
         'I\'m looking for a moderately priced restaurant with Catalan food',
         'What is a cheap restaurant in the south part of town',
         'What about Chinese food',
         'I wanna find a cheap restaurant',
         'I\'m looking for Persian food please',
         'Find a Cuban restaurant in the center',
         'is there a moderately priced restaurant that serves british food',
         'moderately priced restaurant in the south part of town',
         'a cheap mexican restaurant',
         'It doesnt matter']
mode = 'location'

integer = 1
for message in texts:
    found = keywordAlgorithm(message, mode)
    print(str(integer) + " " + found)
    integer += 1