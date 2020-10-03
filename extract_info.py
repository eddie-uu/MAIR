from nltk.corpus import wordnet 
from collections import defaultdict
from extract import extract
import pandas as pd
import numpy as np
import Levenshtein
import re

class extract_info:
    def __init__(self):
        try:
            settings = extract().extract_settings()
            self.edit_dist = int(settings['LEVENSHTEIN_EDIT_DISTANCE']['value'])
        except:
            # Good default value
            self.edit_dist = 3

    def extract_info(self, csv_file, request):
        """
        Main function for extracting the correct restaurant info for a given query.

        @param csv_file: name of the csv file that contains the restaurant info.
        @param request: dictionary (str->str) mapping request types (corresponing to
            column names in the csv) to user inputs for that type. May be empty. 
        """
        data = pd.read_csv(csv_file)
        # Remove "dontcare" coded inputs
        request = {k:v for k,v in request.items() if v != 'dontcare'}
        options = {}
        for pref_type in request:
            # All the different unique options in a column
            options[pref_type] = data[pref_type].dropna().unique()
        for pref_type in request:
            data = self.modify_data(data, pref_type, options, request[pref_type])
        # Shuffle the data
        data = data.sample(frac=1)
        # Prettify
        capt = lambda m: " ".join([word.capitalize() for word in m.split(" ")])
        data["restaurantname"] = data["restaurantname"].apply(capt)
        data["phone"] = data["phone"].apply(self.fix_phone_number)
        data["addr"] = data["addr"].apply(self.add_comma)
        # Can't capitalize a float
        data["addr"] = data["addr"].apply(lambda m: capt(m) if isinstance(m, str) else np.nan)
        return data

    def add_comma(self, address):
        """
        Yes, all this for a comma. It adds a comma after the last mention of road-like
        words, so that you get a prettier address like: "84 Regent Street, City Centre"

        @param address: address string
        """
        if isinstance(address, float):
            return np.nan
        street_types = ["road", "street", "avenue", "lane", "way"]
        for street_type in street_types:
            # We don't want the comma at the end of the address
            if street_type in address and address[-len(street_type):] != street_type:
                comma_index = address.rfind(street_type) + len(street_type)
                address = address[:comma_index] + ',' + address[comma_index:]
                break
        return address

    def fix_phone_number(self, phone_number):
        """
            Makes 11 digit phone numbers look real nice. (others only less ugly)

            @param phone_number: string of a phone number
        """
        # Phone numbers should only contain digits, spaces and dashes
        if isinstance(phone_number, str) and re.match(r"^[0-9 \-]+$", phone_number):
            phone_number = re.sub(r"\D+", '', phone_number)
            if len(phone_number) == 11:
                phone_number = phone_number[:5] + ' ' + phone_number[5:]
                phone_number = phone_number[:9] + ' ' + phone_number[9:]
            return phone_number
        return np.nan

    def modify_data(self, data, pref_type, options, user_input):
        """
            Removes rows from the dataset that do not match the given filter.

            @param data: pandas dataframe containing the restaurant data
            @param pref_type: the preference type (column header) that we're filtering
            @param options: all the different options per preference type
            @param user_input: the input we want to filter by
        """
        user_input = user_input.lower()
        if user_input not in options[pref_type]:
            user_input = self.levenshtein_or_synonym(user_input, options[pref_type])
        return data[0:0] if user_input is None else data.loc[data[pref_type] == user_input]

    def levenshtein_or_synonym(self, word, options):
        """
            Inputs a target word and a list of options. It then chooses one of the
            options that best matches the word, or none of them. It determines this
            based on both synonyms of the target word as well as close spelling 
            errors of the target word and as its synonyms.

            @param word: target word (string)
            @param options: list of candidate words (strings)
        """
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
        # We only need the smallest edit distance
        distances = {op:min(dists) for (op,dists) in distances.items()}
        best = min(distances, key=distances.get)
        if distances[best] <= self.edit_dist:
            return best

if __name__ == "__main__":
    # An example
    # print(extract_info().extract_info("data/restaurant_info.csv", {"pricerange":"expensiive", "area":"center", "food":"thai!"}))
    # print(extract_info().extract_info("data/restaurant_info.csv", {"pricerange":"cheap", "food":"gastropub"}))
    print(extract_info().extract_info("data/restaurant_info.csv", {"pricerange":"moderately", "food":"cuban"}))