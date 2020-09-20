import pandas as pd
import Levenshtein
from nltk.corpus import wordnet 
from collections import defaultdict
import re
import numpy as np

def extract_info(csv_file, request):
    data = pd.read_csv(csv_file)
    request = {k:v for k,v in request.items() if v != 'dontcare'}
    for pref_type in request:
        data = modify_data(data, pref_type, request[pref_type])
    data = data.sample(frac=1)
    capt = lambda m: " ".join([word.capitalize() for word in m.split(" ")])
    data["restaurantname"] = data["restaurantname"].apply(capt)
    data["phone"] = data["phone"].apply(fix_phone_number)
    data["addr"] = data["addr"].apply(add_comma)
    data["addr"] = data["addr"].apply(lambda m: capt(m) if isinstance(m, str) else np.nan)
    return data

def add_comma(address):
    if isinstance(address, float):
        return np.nan
    street_types = ["road", "street", "avenue", "lane", "way"]
    for street_type in street_types:
        print(address[:-len(street_type)])
        print(street_type)
        if street_type in address and address[-len(street_type):] != street_type:
            comma_index = address.rfind(street_type) + len(street_type)
            address = address[:comma_index] + ',' + address[comma_index:]
            break
    return address

def fix_phone_number(phone_number):
    if isinstance(phone_number, str) and re.match(r"^[0-9 \-]+$", phone_number):
        phone_number = re.sub(r"\D+", '', phone_number)
        if len(phone_number) == 11:
            phone_number = phone_number[:5] + ' ' + phone_number[5:]
            phone_number = phone_number[:9] + ' ' + phone_number[9:]
        return phone_number
    return np.nan

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
    print(extract_info("restaurant_info.csv", {"pricerange":"expensive", "area":"centre", "food":"dontcare"}))