import pandas as pd
import Levenshtein
from nltk.corpus import wordnet 
from collections import defaultdict
import re

def extract_info(csv_file, request):
    data = pd.read_csv(csv_file)
    request = {k:v for k,v in request.items() if v != 'dontcare'}
    for pref_type in request:
        data = modify_data(data, pref_type, request[pref_type])
    data = data.sample(frac=1)
    data["restaurantname"] = data["restaurantname"].apply(lambda m: " ".join([word.capitalize() for word in m.split(" ")]))
    # data["phone"] = data["phone"].apply(lambda m: ))
    return data

# def fix_phone_number(phone_number):
#     if re.match("^[0-9 ]+$", myString):

def modify_data(data, pref_type, user_input):
    user_input = user_input.lower()
    options = data[pref_type].dropna().unique()
    if user_input not in options:
        user_input = levenshtein_or_synonym(user_input, options, 3)
    if user_input is None:
        return data
    else:
        return data.loc[data[pref_type] == user_input]

def levenshtein_or_synonym(word, options, threshold):
    save_syns = {}
    # First we check if simply a synonomous word was used
    for op in options:
        synset = wordnet.synsets(op)
        synonyms = [x.lemmas()[0].name() for x in synset]
        if word in synonyms:
            return op
        save_syns[op] = synonyms
    # If not, maybe it was misspelled?
    distances = defaultdict(set)
    for op in options:
        dist = Levenshtein.distance(word, op)
        distances[op].add(dist)
        for alt in save_syns[op]:
            dist = Levenshtein.distance(word, alt)
            distances[op].add(dist)
    distances = {op:max(dists) for (op,dists) in distances.items()}
    best = max(distances, key=distances.get)
    if distances[best] <= threshold:
        return best

if __name__ == "__main__":
    print(extract_info("restaurant_info.csv", {"pricerange":"cheap", "area":"south", "food":"dontcare"}))