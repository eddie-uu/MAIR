from extract import extract_data
import numpy as np
from sklearn.neural_network import MLPClassifier
import pickle
import os
from collections import defaultdict
from sklearn import preprocessing

def mlp(data_file, layers=(16, 32), pickle_file="vectors.pkl", 
        emb_file="fasttext_English.vec", split=0.85, seed=42, 
        print_missing=False):
    """
        Trains a multilayer perceptron (feedforward neural network) on the average 
        word embeddings of labeled sentences.
        By default, uses the FastText model for word embeddings.
        Returns the trained model.

        @param data_file: data file containing labeled sentences. Should be 
            compatible with the extract_data function.
        @param layers: layers of the network. The default values have proven to
            be excellent in testing.
        @param pickle_file: greatly speeds up this function by skipping the step
            of searching through the embedding file. Delete this file if you want
            to use a new embedding file.
        @param emb_file: .vec file containing pre-trained word embeddings.
        @param split: percentage of training data represented as a float between
            0 and 1.
        @param seed: random seed for repreducability.
        @param print_missing: if set to True, prints out sentences from both the
            test and train set that could not be identified due to their words
            not being present in the pre-trained embeddings.
    """
    data = extract_data(data_file, split=split, seed=seed)

    vectors = {}
    words = [word for sentence in data["sentences_train"] for word in sentence]
    words.append([word for sentence in data["sentences_test"] for word in sentence])


    if os.path.exists(pickle_file):
        print("Loading previously saved vectors...")
        with open(pickle_file, 'rb') as f:
            vectors = pickle.load(f)
    else:
        print("Finding vectors...")
        with open(emb_file, 'r', encoding="utf-8") as f:
            for line in f:
                tokens = line.replace('\n','').split(' ')
                # The first line is not an embedding
                if tokens[0] in words and len(tokens) > 2:
                    # Embeddings are saved as numpy arrays
                    vectors[tokens[0]] = np.asarray(list(map(float, tokens[1:])))
        with open(pickle_file, 'wb') as f_pickle:
            pickle.dump(vectors, f_pickle)

    # Training labels should be numerical, and a way to refer back is needed
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
            if print_missing:
                print("The following sentence was not used in training:")
                print(' '.join(sentence))
            continue
        av_vector = sum(sent_vectors) / len(sent_vectors)
        train_vectors.append(av_vector)
        train_labels.append(conv_train_labels[i])

    # Start of alternative code that tries multiple different layer size configs.
    # print("Trying different configurations...")
    # for l1 in range(5, 50, 5):
    #     for l2 in range(10, 100, 10):

    print("Training multilayer perceptron...")
    clf = MLPClassifier(solver='lbfgs', max_iter=1000, alpha=1e-5, hidden_layer_sizes=layers, random_state=seed)
    # sklearn expects standardized data
    scaler = preprocessing.StandardScaler().fit(train_vectors)
    train_vectors = scaler.transform(train_vectors)
    clf.fit(train_vectors, train_labels)

    total = 0
    for sentence, true_label in zip(data["sentences_test"], data["dialog_acts_test"]):
        sent_vectors = []
        for word in sentence:
            if word in vectors:
                sent_vectors.append(vectors[word])
        if sent_vectors == []:
            if print_missing:
                print("The following sentence could not be interpreted and " +
                      "will be trivially classified as null:")
                print(' '.join(sentence))
            predicted_label = "null"
            if predicted_label == true_label:
                total += 1
            continue
        av_vector = sum(sent_vectors) / len(sent_vectors)
        av_vector = scaler.transform([av_vector])
        predicted_id = clf.predict(av_vector)[0]
        predicted_label = id_to_label[predicted_id]
        if predicted_label == true_label:
            total += 1

    print("Accuracy:", total / len(data["sentences_test"]))

if __name__ == "__main__":
    mlp("dialog_acts.dat")