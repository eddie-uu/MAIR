from extract import extract_data
import numpy as np
# from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPClassifier
import pickle
import os
from collections import defaultdict

def mlp():
    data = extract_data("dialog_acts.dat")

    vectors = {}
    words = [word for sentence in data["sentences_train"] for word in sentence]
    words.append([word for sentence in data["sentences_test"] for word in sentence])


    if os.path.exists("vectors.pkl"):
        print("Loading previously saved vectors...")
        with open("vectors.pkl", 'rb') as f:
            vectors = pickle.load(f)
    else:
        print("Finding vectors...")
        with open("fasttext_English.vec", 'r', encoding="utf-8") as f:
            for line in f:
                tokens = line.replace('\n','').split(' ')
                # We check if the word on this line is one of the words we want.
                # We also skip the first line which has the number of words and 
                # dimensions of the embeddings.
                if tokens[0] in words and len(tokens) > 2:
                    # We save vectors as a numpy array of floats.
                    vectors[tokens[0]] = np.asarray(list(map(float, tokens[1:])))
        with open("vectors.pkl", 'wb') as f_pickle:
            pickle.dump(vectors, f_pickle)

    temp = defaultdict(lambda: len(temp)) 
    conv_train_labels = [temp[ele] for ele in data["dialog_acts_train"]] 

    id_to_label = {}
    for i, ident in enumerate(conv_train_labels):
        id_to_label[ident] = data["dialog_acts_train"][i]

    train_vectors = []
    train_labels = []
    for i, sentence in enumerate(data["sentences_train"]):
        sent_vectors = []
        for word in sentence:
            if word in vectors:
                sent_vectors.append(vectors[word])
        if sent_vectors == []:
            # print("!!!!!!!!!!!!!!!!")
            # print(sentence)
            continue
        av_vector = sum(sent_vectors) / len(sent_vectors)
        train_vectors.append(av_vector)
        train_labels.append(conv_train_labels[i])


    # print("Trying different configurations...")
    # for l1 in range(10, 100, 10):
    #     for l2 in range(5, 50, 5):
            # print(l1, l2)
    clf = MLPClassifier(solver='lbfgs', max_iter=1000, alpha=1e-5, hidden_layer_sizes=(20, 30), random_state=1)
    clf.fit(train_vectors, train_labels)

    total = 0
    for sentence, true_label in zip(data["sentences_test"], data["dialog_acts_test"]):
        sent_vectors = []
        for word in sentence:
            if word in vectors:
                sent_vectors.append(vectors[word])
        if sent_vectors == []:
            predicted_label = "null"
            if predicted_label == true_label:
                total += 1
            continue
        av_vector = sum(sent_vectors) / len(sent_vectors)
        predicted_id = clf.predict([av_vector])[0]
        predicted_label = id_to_label[predicted_id]
        if predicted_label == true_label:
            total += 1

    print("Accuracy:", total / len(data["sentences_test"]))

if __name__ == "__main__":
    mlp()