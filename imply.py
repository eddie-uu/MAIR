from pyswip import Prolog
import os
import pandas as pd
import re
from extract_info import extract_info
from extract import extract
import csv
from collections import defaultdict

class Implications():

    def __init__(self, impl_file="data/implications.tsv", data_file="data/restaurant_info.csv"):
        settings = extract().extract_settings()
        if str(settings["PROLOG"]["value"]) == "True":
            self.prolog = True
            self.convert_to_prolog(rule_file=impl_file, fact_file=data_file)
        else:
            self.prolog = False
            self.rules = self.convert_to_python(impl_file)
        if str(settings["PRINT_REASONING"]["value"]) == "True":
            self.print_r = True
        else:
            self.print_r = False

    def __call__(self, requirements, request):
        # TODO: Make sure "quality" is actually in the request, not the requirements
        restaurants = extract_info().extract_info("data/restaurant_info.csv", request)
        if requirements == []:
            return restaurants
        if self.prolog:
            return self.implications_prolog(requirements, request.values(), restaurants)
        else:
            return self.implications_python(requirements, restaurants)

    def convert_to_prolog(self, prolog_file="data/implications.pl", fact_file="data/restaurant_info.csv", 
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
        self.sort_file(prolog_file)
        return True

    def sort_file(self, filename):
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

    def convert_to_python(self, impl_file="data/implications.tsv"):
        rules = []
        with open(impl_file, newline='') as tsv_file:
            r = csv.reader(tsv_file, delimiter='\t')
            next(r)
            for row in r:
                antecedent = set(row[1].split(', '))
                consequent = row[:1] + row[2:]
                rules.append((antecedent, consequent))
        return rules

    def implications_python(self, requirements, restaurants):
        histories = []
        results = []
        for rest_dict in restaurants.to_dict('records'):
            facts = {rest_dict["pricerange"], rest_dict["area"], rest_dict["food"], rest_dict["quality"]}
            result, history = self.apply_rules(facts, [rest_dict["restaurantname"]])
            if set(requirements).issubset(result.union(facts)):
                results.append(rest_dict["restaurantname"])
            histories.append(history)
        if self.print_r:
            self.print_histories(histories, requirements)
        return restaurants.loc[restaurants["restaurantname"].isin(list(results))]

    def print_histories(self, histories, requirements):
        if histories == []:
            print("No restaurants comply with your initial request, and " + 
                  "therefore non comply with your newly added requirements either.")
            return
        print("What follows is the reasoning steps used for determining for each" +
              " of your remaining restaurants whether they comply with your newly" +
              " added requirements.")
        for history in histories:
            print(f"\n\n>> {history[0]}\n")
            if len(history) == 1:
                print("For this restaurant, no rules could be applied. As such," +
                " we cannot say whether it complies with any of your requirements.")
                continue
            print("> Rules used:")
            history = history[1:]
            consequents = set()
            for rule_id in history:
                for antecedent, consequent in self.rules:
                    if consequent[0] == rule_id:
                        ant_print = " and ".join(antecedent)
                        print(f"Per rule {rule_id}: {ant_print} -> {consequent[1]} = {consequent[2]}")
                        if consequent[2] == "True":
                            consequents.add(consequent[1])
                        else:
                            consequents.add("not " + consequent[1])
                        break
            print("\n> Conclusions for each of your requirements:")
            for req in requirements:
                if req in consequents:
                    base_type = True
                    if req[:4] == "not ":
                        req = req[4:]
                        base_type = False
                    if "not " + req in consequents and base_type:
                        print("Your requirement that the restaurant has the " +
                              f"attribute '{req}' was determined to be both " +
                              "true and not true. For the purpose of this " +
                              "recommendation system, we assume that in such " +
                              "a case the requirement is satisfied, so that you" +
                              " can make your own judgment.")
                    elif "not " + req in consequents:
                        print("Your requirement that the restaurant has the " +
                              f"attribute 'not {req}' was determined to be both " +
                              f"true and not true (since {req} was also inferred)." +
                              " For the purpose of this recommendation system, we" +
                              " assume that in such a case the requirement is " +
                              "satisfied, so that you can make your own judgment.")
                    elif base_type:
                        print(f"Your requirement that '{req}' is true for this " +
                              "restaurant was satisfied!")
                    else:
                        print(f"Your requirement that '{req}' is false for this " +
                              "restaurant was satisfied!")
                else:
                    if req[:4] == "not " and req[4:] in consequents or "not " + req in consequents:
                        print(f"The opposite of your requirement that '{req}' holds.")
                    else:
                        # Note: just because we couldn't derive a requirement, we cannot
                        # make a judgment on its truth value (since the premises are
                        # sufficient, but not necessary).
                        print("Based on the available inferences, we cannot say " +
                            f"whether '{req}' holds for this restaurant.")
            
    def apply_rules(self, facts, history):
        for antecedent, consequent in self.rules:
            if consequent[2] == "False":
                cons_to_add = "not " + consequent[1]
            else:
                cons_to_add = consequent[1]
            if antecedent.issubset(facts) and cons_to_add not in facts:
                facts.add(cons_to_add)
                history.append(consequent[0])
                return self.apply_rules(facts, history)
        return facts, history

    def implications_prolog(self, requirements, base_req, restaurants):
        """
        Makes a Prolog query based on the requirements of the user. Returns the 
        corresponding restaurants as a pandas array, like in extract_info.

        @param requirements: list of requirements that should hold. These correspond
            to the Prolog functors' syntax, apart from the spaces.
        @param base_req: list containing the three basic requirements: area, 
            foodtype and pricerange. May be partial/empty. 
        @param restaurants: Pandas array containing all restaurants still under 
            consideration.
        """
        prolog = Prolog()
        prolog.consult("data/implications.pl")
        # Let's build a query that Prolog can understand
        prolog_query = ''.join([fact + "(X)," for fact in base_req])
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
    impl = Implications()
    print(impl(["good restaurant"], {"pricerange":"expensive", "area":"centre"}))
    # print(impl(["romantic"], {"pricerange":"cheap", "quality":"good food"}))