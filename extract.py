import random

with open("dialog_acts.dat") as f:
    data = f.readlines()

data = [sentence[:-1] for sentence in data]

# random.shuffle(data)

train_size = round(len(data) * 0.85)
training = data[:train_size]
test = data[train_size:]

dialog_acts_train = [sentence.split(' ')[0] for sentence in training]
sentences_train = [sentence.split(' ')[1:] for sentence in training]
dialog_acts_test = [sentence.split(' ')[0] for sentence in test]
sentences_test = [sentence.split(' ')[1:] for sentence in test]

