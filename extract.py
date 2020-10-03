import random
import json
import time
import re

class extract:
    def __init__(self, file_name = '', split=0.85, seed=42):
        if (file_name != ''):
            """
                Extracts data from the .dat file, shuffles it and makes a train/test
                split. Returns a dictionary mapping names to the corresponding lists.
                sentences_train and sentences_test are the randomly shuffled sentences
                in the form of lists of words. dialog_acts_train and dialog_acts_test 
                are the dialog acts in the order that corresponds to the indices of the 
                sentences. They are lists of strings.
                Note that the data should be in the form of one sentence per line with 
                the label in front if it seperated by a space.

                @param file_name: name of the data file
                @param split: the data split of the traing/test set, between 0 and 1.
                    Represents the percentage of the training set.
                @param seed: random seed to reproduce results.
            """
            if split < 0 or split > 1:
                raise ValueError("Incorrect split ratio!")

            with open(file_name) as f:
                data = f.readlines()

            data = [sentence[:-1] for sentence in data]

            random.seed(seed)
            random.shuffle(data)

            train_size = round(len(data) * split)
            training   = data[:train_size]
            test       = data[train_size:]

            self.dialog_acts_train = [sentence.split(' ')[0] for sentence in training]
            self.sentences_train   = [sentence.split(' ')[1:] for sentence in training]
            self.dialog_acts_test  = [sentence.split(' ')[0] for sentence in test]
            self.sentences_test    = [sentence.split(' ')[1:] for sentence in test]

    def configure_settings(self):
        """
        Allows changing of settings.
        """
        settings = self.extract_settings()

        finishedSettings = False
        while not finishedSettings:
            print("Which setting would you like to change?")
            counter = 1
            settingsIndex = {}

            for setting in settings:
                print(str(counter) + ". " + settings[setting]["text"])
                settingsIndex[str(counter)] = {"key": setting, "value": settings[setting]} 
                counter += 1
            
            saveAndRestart = counter
            cancel = counter + 1
            print(str(saveAndRestart) + ". Save and close")
            print(str(cancel) + ". Cancel")

            choice = input("> ")

            if (choice == str(saveAndRestart)):
                finishedSettings = True
                self.__change_settings(settings)
                print("Configurations have been saved, closing applications, new settings will be used during next startup...")
            elif (choice == str(cancel)):
                finishedSettings = True
                print("Configurations will remain the same, closing applications, new settings will be used during next startup..")
            elif choice in settingsIndex:
                settingKey = settingsIndex[choice]["key"]
                settingValues = settingsIndex[choice]["value"]

                validChoices = {"int": "^\d+$", "bool": 'true|false|True|False|TRUE|FALSE'}
                print("Current setting for " + str(settingKey) + " is: " + str(settingValues["value"]))
                print("To which value would you like to change this? (Value must be of the type: " + str(settingValues["valueType"]) + " )")

                if (settingValues["valueType"] == "ENUM"):
                    enumOptions = ""
                    for option in settingValues["valueOptions"]:
                        print("- " + str(option["value"]))
                        enumOptions += str(option["value"]).lower() + "|"
                    validChoices["ENUM"] = enumOptions[:-1] if len(enumOptions) > 0 else enumOptions

                choice = input("> ")

                pattern = re.compile(validChoices[str(settingValues["valueType"])])
                if pattern.match(choice) != None:
                    print("Settings for " + settingKey + " have been changed from " + str(settingValues["value"]) + " to " + choice)
                    settings[settingKey]["value"] = choice
                else:
                    print("Sorry, the given input is invalid")
                time.sleep(1)
            else:
                print("Sorry, the given input could not be recognized")
                time.sleep(1)

    def extract_settings(self):
        settings_file = open("data/settings.json", "r")
        json_object   = json.load(settings_file)
        settings_file.close()
        return json_object

    def __change_settings(self, configuration):
        settings      = json.dumps(configuration, indent=4)
        settings_file = open("data/settings.json", "w")
        settings_file.write(settings)
        settings_file.close()