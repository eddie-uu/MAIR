from abstract_mla import abstract_machine_learning_algorithm
from extract import extract
from collections import defaultdict, Counter
from sklearn import preprocessing
from sklearn.neural_network import MLPClassifier
import numpy as np
import pickle
import os
from extract import extract

class multi_layer_perceptron(abstract_machine_learning_algorithm):
    def __init__(self):
        settings = extract().extract_settings()
        if str(settings["PRINT_MLP_F1"]["value"]) == "True":
            self.print_f1 = True
        else:
            self.print_f1 = False
    
    def mlp(self, data_file, layers=(16, 32), pickle_file="data/vectors.pkl", 
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
        data = extract(data_file, split=split, seed=seed)

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

        print("Training multilayer perceptron...\n")
        clf = MLPClassifier(solver='lbfgs', max_iter=1000, alpha=1e-5, hidden_layer_sizes=layers, random_state=seed)
        # sklearn expects standardized data
        scaler = preprocessing.StandardScaler().fit(train_vectors)
        train_vectors = scaler.transform(train_vectors)
        clf.fit(train_vectors, train_labels)
        
        to_save = []
        # For F1 score, maps predicted classes to their actual correct counts.
        counts_per_class = {c:Counter() for c in id_to_label.values()}

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

            counts_per_class[predicted_label][true_label] += 1

            if predicted_label == true_label:
                total += 1
            else:
                to_save.append((sentence, true_label, predicted_label))

        # Save incorrectly labeled answers for manual inspection
        with open("data/wrong_answers_mlp.txt", 'w') as f:
            for sent_tuple in to_save: 
                f.write(f"{' '.join(sent_tuple[0])} -- Predicted: {sent_tuple[1]} -- Actually: {sent_tuple[2]}\n")
        
        if self.print_f1:
            self.f1_score(counts_per_class)

        print("\nOverall accuracy:", round(total / len(data.sentences_test), 4))

        return clf, id_to_label, scaler
        
    def f1_score(self, counts_per_class):
        """
        Prints the precision, recall and F1 scores given the classification.

        @param counts_per_class: dictionary, maps classes predicted by the model
            to counters with the real labels of items in the given class.
        """
        totals = [0,0,0]
        usable_labels = 0

        for label, count_dict in counts_per_class.items():
            true_pos = count_dict[label]
            positives = sum(count_dict.values())
            if positives == 0:
                print(f"The label '{label}' was never never chosen by the algorithm.")
                print("As such, it will not be considered in the averages.\n")
                continue
            precision = true_pos / positives
            label_total = sum(cnt[label] for cnt in counts_per_class.values())
            if label_total == 0:
                print(f"The label '{label}' is not in the test set.")
                print("As such, it will not be considered in the averages.\n")
                continue
            recall = true_pos / label_total
            f1 = 2 * precision * recall / (precision + recall)
            print(f"'{label}' has a precision of {round(precision,4)} and a recall " +
                  f"of {round(recall,4)}. F1 score is {round(f1,4)}.\n")
            totals[0] += precision
            totals[1] += recall
            totals[2] += f1
            usable_labels += 1
        
        av_prec = totals[0] / usable_labels
        av_rec = totals[1] / usable_labels
        av_f1 = totals[2] / usable_labels
        print(f"\nAverage precision per predicted class is {round(av_prec,4)}, " +
              f"recall {round(av_rec,4)} and F1 {round(av_f1,4)}.")
        

    def predict(self, input_sentence, model, scaler, id_to_label=None, pickle_file="data/vectors.pkl"):
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
        av_vector = np.zeros((vec_len,)) if sent_vectors == [] else sum(sent_vectors) / len(sent_vectors)
        av_vector = scaler.transform([av_vector])
        pred_id = model.predict(av_vector)[0]
        
        return pred_id if id_to_label is None else id_to_label[pred_id]

    def mlp_loop(self):
        """
            Loads a model as desinged by mlp(), then starts a user interface where
            the user can type sentences to be classified.
        """
        if os.path.exists("data/mlp_model.pkl"):
            model, id_dict = pickle.load("data/mlp_model.pkl")
        else:
            model, id_dict, scaler = self.mlp("data/dialog_acts.dat")
        print("You can quit by typing 'bye'.")
        while True:
            sentence = input("Please write your sentence here:\n")
            if sentence == "bye":
                break
            prediction = self.predict(sentence, model, scaler, id_dict)
            print(f"We predict your sentence belongs to the {prediction} class.")

    def perform_algorithm(self, testing):
        self.mlp("data/dialog_acts.dat") if testing else self.mlp_loop()

if __name__ == "__main__":
    # Run this file to save a trained model.
    mlp = multi_layer_perceptron()
    model, id_to_label, scaler = mlp.mlp("data/dialog_acts.dat")
    with open("data/mlp_model.pkl", 'wb') as f_pickle:
        pickle.dump((model, id_to_label, scaler), f_pickle)
    # Example use:
    # print(mlp.predict("how about a turkish restaurant in the center", model, scaler, id_to_label))
