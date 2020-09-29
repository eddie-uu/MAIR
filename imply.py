from pyswip import Prolog
import os
import pandas as pd
import re
from extract_info import ExtractInfo

def convert_to_prolog(prolog_file="data/implications.pl", fact_file="data/restaurant_info.csv", 
                      fact_data=None, rule_file="data/implications.tsv"):
    """
        Converts the rules in implications.tsv and the facts from restaurant_info.csv
        into a Prolog file.

        @param prolog_file: path to the output Prolog file.
        @param fact_file: path to the file with restaurant info.
        @param fact_data: alternatively, a pandas dataframe as extracted from the
            same type of file.
        @param rule_file: path to the file containing the rules (implications).
    """
    if os.path.exists(prolog_file):
        return False
    if not os.path.exists(rule_file):
        return False
    if fact_data is None:
        if os.path.exists(fact_file):
            fact_data = pd.read_csv(fact_file)
        else:
            return False
    rule_data = pd.read_csv(rule_file, sep='\t')

    # We'll delete columns we don't need, so we can eventually write only the 
    # columns we need in Prolog to the file
    del fact_data["phone"]
    del fact_data["addr"]
    del fact_data["postcode"]
    # Prolog functors can't contain spaces
    fact_data = fact_data.replace(' ', '_', regex=True)
    # Facts will be of the form type(name).
    fact_data["pricerange"] += '(' + fact_data["restaurantname"] + ').'
    fact_data["area"] += '(' + fact_data["restaurantname"] + ').'
    fact_data["food"] += '(' + fact_data["restaurantname"] + ').'
    fact_data["quality"] += '(' + fact_data["restaurantname"] + ').'
    del fact_data["restaurantname"]
    # Write the facts to the Prolog file
    fact_data.to_csv(prolog_file, sep='\n', index=False, header=False)

    del rule_data["id"]
    del rule_data["level"]
    del rule_data["description"]
    # The bodies of the rules need to be of the form a(X), b(X) etc.
    rule_data["antecedent"] = rule_data["antecedent"].apply(lambda x: re.sub(r'(?=,)', r'(X)', str(x)))
    rule_data["antecedent"] = rule_data["antecedent"].apply(lambda x: re.sub(r'(?<!,) ', r'_', str(x)))
    # You could negate terms with not, but then inferences with a single premise
    # would not work if that premise would be negated.
    # rule_data["antecedent"] = rule_data["antecedent"].apply(lambda x: re.sub(r'not_', r'\+ ', str(x)))
    # Prolog terms end in a full stop.
    rule_data["antecedent"] += '(X).'
    # Now for the heads of the rules
    rule_data["consequent"] = rule_data["consequent"].replace(' ', '_', regex=True)
    # Heads will not be negated, but rather "if A then not B" will be interpreted
    # as adding "not B" as a separate functor.
    # Note that a solution where it's actually negated doesn't make sense when
    # working with Prolog. It is also intuitive: A holds under certain conditions,
    # not A under certain other conditions, and we simply don't know whether A holds
    # or not under all other conditions. So as an example, from the rule
    # busy -> not romantic we can imply that when it is busy it is not romantic,
    # but not that this is the only situation where that holds.
    mask = (rule_data["truth"] == False)
    rule_data.loc[mask, "consequent"] = "not_" + rule_data["consequent"]
    # Truning it into an actual Prolog rule
    rule_data["consequent"] += '(X) :- ' + rule_data["antecedent"]
    del rule_data["antecedent"]
    del rule_data["truth"]
    # Add the rules to the same file the facts are in
    rule_data.to_csv(prolog_file, sep='\n', index=False, header=False, mode='a')

    # Prolog wants clauses to be together
    sort_file(prolog_file)
    return True

def sort_file(filename):
    """
        Sorts a file alphabetically.

        @param filename: path to file.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    with open(filename, 'w') as f:
        for line in sorted(lines):
            if any(c.isalpha() for c in line):
                f.write(line)

def implications(requirements, request):
    """
    Makes a Prolog query based on the rewuirements of the user. Returns the 
    corresponding restaurants as a pandas array, like in extract_info.

    @param requirements: list of requirements that should hold. These correspond
        to the Prolog functors' syntax, apart from the spaces.
    @param request: dictionary (str->str) mapping request types (corresponing to
        column names in the csv) to user inputs for that type. May be empty. 
    """
    restaurants = ExtractInfo().extract_info("data/restaurant_info.csv", request)
    if requirements == []:
        return restaurants
    convert_to_prolog()
    prolog = Prolog()
    prolog.consult("data/implications.pl")
    # Let's build a query that Prolog can understand
    prolog_query = ''.join([fact + "(X)," for fact in request.values()])
    prolog_query += "(X),".join(requirements) + "(X)."
    prolog_query = prolog_query.replace(' ', '_')
    # Send to Prolog!
    answer = list(prolog.query(prolog_query))
    # We only used one variable
    answer = [x['X'] for x in answer]
    # Capitalize and replace underscores by spaces
    answer = [' '.join([word.capitalize() for word in x.split('_')]) for x in answer]
    return restaurants.loc[restaurants["restaurantname"].isin(answer)]

if __name__ == "__main__":
    # An example
    print(implications(["good restaurant"], {"pricerange":"expensive", "area":"centre"}))