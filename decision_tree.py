from sklearn import datasets
from sklearn import tree
from sklearn.tree import export_text
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from extract import extract_data
import numpy as np

# Parsed data from "dialog_acts.dat", with 85% training data
data              = extract_data("dialog_acts.dat", 0.95) # 85

# Array of values from each data key
dialog_acts_train = data["dialog_acts_train"]
sentences_train   = data["sentences_train"]
sentences_train   = [[" ".join(sentence)] for sentence in sentences_train]
dialog_acts_test  = data["dialog_acts_test"]
sentences_test    = data["sentences_test"]
sentences_test   = [[" ".join(sentence)] for sentence in sentences_test]

oneHotEncoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
oneHotEncoder.fit(sentences_test) # sentences_train
oneHotLabels = oneHotEncoder.transform(sentences_test) # sentences_train

decisionTreeClassifier = tree.DecisionTreeClassifier()
decisionTreeClassifier = decisionTreeClassifier.fit(oneHotLabels, dialog_acts_test) #dialog_acts_train

prediction = oneHotEncoder.transform([["thank you good bye"]]) # TODO: CMD input
print(decisionTreeClassifier.predict(prediction))