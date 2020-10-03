from extract import Extract
from collections import defaultdict
from sklearn import preprocessing
from sklearn.neural_network import MLPClassifier
import numpy as np
import pickle
import os

def mlp(data_file, layers=(16, 32), pickle_file="data/vectors.pkl", 
        emb_file="data/fasttext_English.vec", split=0.85, seed=42, 
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
    data = Extract(data_file, split=split, seed=seed)

    vectors = {}
    words = [word for sentence in data.sentences_train for word in sentence]
    words.append([word for sentence in data.sentences_test for word in sentence])

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
    conv_train_labels = [temp[ele] for ele in data.dialog_acts_train] 
    id_to_label = {}
    for i, ident in enumerate(conv_train_labels):
        id_to_label[ident] = data.dialog_acts_train[i]

    train_vectors = []
    train_labels = []
    for i, sentence in enumerate(data.sentences_train):
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
    
    to_save = []

    total = 0
    for sentence, true_label in zip(data.sentences_test, data.dialog_acts_test):
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
        else:
            to_save.append((sentence, true_label, predicted_label))

    with open("data/wrong_answers_mlp.txt", 'w') as f:
        for sent_tuple in to_save: 
            f.write(f"{' '.join(sent_tuple[0])} -- Predicted: {sent_tuple[1]} -- Actually: {sent_tuple[2]}\n")

    print("Accuracy:", total / len(data.sentences_test))
    return clf, id_to_label, scaler

def mlp_test(model, input_sentence, scaler, id_to_label=None, pickle_file="data/vectors.pkl"):
    """
        Predicts the label of a sentence based on a pre-trained machine learning
        model. Ignores words not found in the train or test set.

        @param model: pre-trained scikit-learn machine learning model.
        @param input sentence: sentence to predict the label of. (string)
        @param id_to_label: optional, dictionary converting class identifiers 
            to class labels.
        @param pickle_file: as in mlp(), speedily gets the training vectors
    """
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as f:
            vectors = pickle.load(f)
    input_sentence = input_sentence.lower().split(' ')
    # Almost certainly 300
    vec_len = len(vectors["the"])
    sent_vectors = []
    for word in input_sentence:
        if word in vectors:
            sent_vectors.append(vectors[word])
    
    # Set base vector to all zeroes
    av_vector = [np.zeros((vec_len,))] if sent_vectors == [] else sum(sent_vectors) / len(sent_vectors)
    av_vector = scaler.transform([av_vector])
    pred_id = model.predict(av_vector)[0]
    
    return pred_id if id_to_label is None else id_to_label[pred_id]

def mlp_loop():
    """
        Loads a model as desinged by mlp(), then starts a user interface where
        the user can type sentences to be classified.
    """
    if os.path.exists("data/mlp_model.pkl"):
        model, id_dict = pickle.load("data/mlp_model.pkl")
    else:
        model, id_dict, scaler = mlp("data/dialog_acts.dat")
    print("You can quit by typing 'stop'.")
    while True:
        sentence = input("Please write your sentence here:\n")
        if sentence == "stop":
            break
        prediction = mlp_test(model, sentence, scaler, id_dict)
        print(f"We predict your sentence belongs to the {prediction} class.")

if __name__ == "__main__":
    # Run this file to save a trained model.
    model, id_to_label, scaler = mlp("data/dialog_acts.dat")
    with open("data/mlp_model.pkl", 'wb') as f_pickle:
        pickle.dump((model, id_to_label, scaler), f_pickle)
    # Example use:
    print(mlp_test(model, "no", scaler, id_to_label))