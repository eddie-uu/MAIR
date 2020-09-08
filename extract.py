import random

def extract_data(file_name, split=0.85, seed=42):
    """
        Extracts data from the .dat file, shuffles it and makes a train/test
        split. Returns a dictionary mapping names to the corresponding lists.
        sentences_train and sentences_test are the randomly shuffled sentences
        in the form of lists of words. dialog_acts_train and dialog_acts_test 
        are the dialog acts in the order that corresponds to the indices of the 
        sentences. They are lists of strings.

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

