import random
import json

def extract_data(file_name, split=0.85, seed=42):
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
    training = data[:train_size]
    test = data[train_size:]

    dialog_acts_train = [sentence.split(' ')[0] for sentence in training]
    sentences_train = [sentence.split(' ')[1:] for sentence in training]
    dialog_acts_test = [sentence.split(' ')[0] for sentence in test]
    sentences_test = [sentence.split(' ')[1:] for sentence in test]

    return {"dialog_acts_train":dialog_acts_train, "sentences_train":sentences_train,
            "dialog_acts_test":dialog_acts_test, "sentences_test":sentences_test}

def extract_settings():
    settings_file = open("settings.json", "r")
    json_object = json.load(settings_file)
    settings_file.close()
    
    # for key in json_object.keys():
    #    print(key)
    
    return json_object

def change_setting(setting, value):
    settings_file = open("settings.json", "r")
    json_object = json.load(settings_file)
    settings_file.close()
    
    json_object[setting]["value"] = value
    settings = json.dumps(json_object, indent=4)
    settings_file = open("settings.json", "w")
    settings_file.write(settings)
    settings_file.close()

# change_setting('CORRECTNESS_LEVENSHTEIN', "False")
# settings = extract_settings()