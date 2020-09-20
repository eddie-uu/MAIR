import re
def checkPattern(text, patterns, defaultValue = ''):
    for pattern in patterns:
        match = re.search(pattern['pattern'], text)
        if match:
            text = match.group(pattern['group']) if defaultValue == '' else defaultValue 
    return text

def keywordAlgorithm(text, mode = ''):
    response = {'history': []}
    text = text.lower()
    baseDontCarePatterns = [{'pattern': 'doesnt matter'}, {'pattern': 'dont care'}]
    
    if mode == 'price' or mode == '':
        pricePatterns = [{'pattern': '(cheap)', 'group': 1},
                         {'pattern': '(moderately)', 'group': 1},
                         {'pattern':'(expensive)', 'group': 1}]
        priceDontCarePatterns = baseDontCarePatterns
        priceDontCarePatterns.append({'pattern': 'any price'})
        
        result = checkPattern(text, pricePatterns)
        endResult = checkPattern(result, priceDontCarePatterns, 'dontcare')
        if len(endResult.split()) < 2 and endResult != '':
            text = text if endResult == 'dontcare' else text.replace(result, '')
            text = text.replace(' priced ', '')
            response['priceRange'] = endResult

    if mode == 'location' or mode == '':
        areaPatterns = [{'pattern': '(center)', 'group': 1},
                        {'pattern': '(north)', 'group': 1},
                        {'pattern': '(south)', 'group': 1},
                        {'pattern': '(east)', 'group': 1},
                        {'pattern': '(west)', 'group': 1}]
        areaDontCarePatterns = baseDontCarePatterns
        areaDontCarePatterns.append({'pattern': 'any area'})
        areaDontCarePatterns.append({'pattern': 'any part'})

        result = checkPattern(text, areaPatterns)
        endResult = checkPattern(result, areaDontCarePatterns, 'dontcare')

        if len(endResult.split()) < 2 and endResult != '':
            text = text if endResult == 'dontcare' else text.replace(result, '')
            response['area'] = endResult

    if mode == 'food' or mode == '':
        foodPatterns = [{'pattern': '(.+?) (food)', 'group': 1},
                        {'pattern': '(serving|serves|serve) (.*)', 'group': 2},
                        {'pattern': '(with|about) (.*)', 'group': 2},
                        {'pattern': '(for|a) (.*)', 'group': 2},
                        {'pattern': '(.+?) (restaurant)', 'group': 1}]
        foodDontCarePatterns = baseDontCarePatterns
        foodDontCarePatterns.append({'pattern': 'any type'})

        result = checkPattern(text, foodPatterns)
        endResult = checkPattern(result, foodDontCarePatterns, 'dontcare')
        
        foodType = True
        for words in endResult.split():
            if len(words) < 3: foodType = False

        if foodType and endResult != '':
            response['food'] = endResult
    
    return response

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
mode = ''

integer = 1

for message in texts:
    found = keywordAlgorithm(message, mode)
    print(str(integer) + " " + str(found))
    integer += 1
