# MAIR RestRec
This project implements a restaurant recommendation system based on both labeled 
user queries and a database of restaurants in Cambridge. The system works as a 
command line program, where the user can type in queries and interact with the 
system in different ways.

Github: https://github.com/eddie-uu/MAIR.

## Setup
### You will need Python version 3.6 or higher.
### The following libraries need to be installed for succesfull execution of the project:
* scikit-learn
* pandas
* python-levenshtein
* nltk
* numpy
* pyswip

All these can be installed using

`pip install <package-name>`

### Other dependencies:
If you have not downloaded it before, make sure to run the following line once in Python:

`nltk.download('wordnet')`

You will also need SWI Prolog version 7.2 or higher installed. See https://www.swi-prolog.org/Download.html.

All testing of this code has been on Windows 10, no guarantees for other operating systems/versions.

## Start
In order to start the application, navigate to the main directory of this project 
and type the following command in your console to start the execution:

`python main.py`

At first, you will be presented with 8 different options. Type the number (1-8) to use 
the system in the corresponding way. See section on `main.py` for more information.

For inspiration, you can view example dialogs with the system in `examples.txt`.

## Files

### `main.py`

The main file is used as a disambiguation for how the user wants to interact with the system.
There are 8 options:

1. Test baseline: runs a test on the baseline system, and prints out the resulting performance metrics.
2. Test decision tree: if `decision_tree.pkl` does not exist, trains the decision tree. Then also prints out performance metrics.
3. Test neural network: trains the multilayer perceptron (this doesn't take very long), then prints out performance metrics.
4. Baseline: allows the user to type sentences that will be classified by the baseline systems.
5. Decision tree: if `decision_tree.pkl` does not exist, trains the decision tree. Allows the user to type sentences that will be classified by the decision tree.
6. Neural network: if `decision_tree.pkl` does not exist, trains the multilayer perceptron. Allows the user to type sentences that will be classified by the MLP.
7. Dialog: start the main dialog system.
8. Change settings: lets the user change the settings of the dialog system.

### `dialog_flow.py`

The main file for running the dialog system. Contains the `dialog_flow` class that takes care
of all high-level processes and (almost) all user interaction. All other classes are invoked by 
this class at various points to execute low-level tasks that are necessary during the dialog.
See the top of this file for more information.

### `extract.py`

Contains the `extract` class, which has two functions. First, it can processes the data
from `dialog_acts.dat` and perform a train/test split. Second, it can process the settings
from `settings.json` and make sure that their current values can be accessed by other classes.

### `abstract_mla.py`

Abstract class used as a recipe for the algorithms in the following three files.

### `baseline_systems.py`

Implements a majority and a rule-based system as comparisons for the systems implemented
in `decision_tree.py` and `mlp.py`.

### `decision_tree.py`

Includes the `decision_tree` class, which is used to train a decision tree on the data from 
`dialog_acts.dat`. You can use option 2 in `main.py` to pre-train this model so that the 
results will be saved to `decision_tree.pkl`.

### `mlp.py`

Includes the `multi_layer_perceptron` class, which is used to train a multilayer perceptron
(a type of feedforward neural network) on the data from `dialog_acts.dat` using word embeddings
from `vectors.pkl` or `fasttext_English.vec`. You can run this file once via the command line to
make sure training does not need to take place at execution time. If you already have a version of
`mlp_model.pkl`, this is not necessary. Also includes functions for using a pre-trained model, 
testing out a model and for printing evaluation measures.

### `keyword_algorithm.py`

Includes the `keyword_algorithm` class, which is used to extract user preferences from user utterances.

### `extract_info.py`

Includes the `extract_info` class, which is used to extract information from `restaurant_info.csv`,
based on translated queries from `keyword_algorithm.py`, in the form of Pandas dataframes.

### `imply.py`

Includes the `Implications` class, which is used to find restaurants that comply with further 
requirements beyond the base requirements from `restaurant_info.csv`. Running this file directly
on the command line produces the example mentioned in the report.

### `data/all_dialogs.txt`

Contains all unedited dialogs used for training. Not used in the code, but useful for reference.

### `data/decision_tree.pkl`

Pickle file in order to be able to use a pretrained decision tree model at dialog execution time.
Make sure to delete this file if you change `dialog_acts.dat`. You can produce this file by running
`main.py` and choosing option 2.

### `data/dialog_acts.dat`

Preprocessed training data for training the dialog classifiers. First word on a line is the label.

### `data/examples.txt`

Contains a few example interactions with the dialogue system. The examples are chosen to show a range
of what the system is capable of.

### `data/fasttext_English.vec`

**FILE NOT INCLUDED**

Pre-trained FastText word embeddings. You can download this file at https://fasttext.cc/docs/en/crawl-vectors.html.
Search for English, text version, and make sure to extract the gz file on a Linux-based system.
The file is about 2.2 GB, and can be used by `mlp.py` to extract the necessary vectors. Note
that this takes quite a long time. You can also substitute this file for different pre-trained 
word embeddings in the same format.

### `data/implications.pl`

Precomputed Prolog knowledge base used by `implications.py`. Make sure to delete this file if you 
change either `restaurant_info.csv` or `implications.tsv`. Note that you can also query this
knowledge base by consulting this file in Prolog.

### `data/implications.tsv`

Tab-separated file containing reasoning rules used by `implications.py`. Inspection of this file
also provides a description of each rule.

### `data/mlp_model.pkl`

**FILE NOT INCLUDED**

Pickle file in order to be able to use a pretrained multilayer perceptron model at dialog execution time.
Make sure to delete this file if you change either `dialog_acts.dat` or want to use another word embedding file.
Note that this file is not included due to the fact that whether you can import it depends on whether your 
version of scikit-learn is the same as whoever produced the file. To generate the file before executing the
main program you can run `mlp.py`. The file can also be produced at execution time, or by choosing option
3 in `main.py`.

### `data/restaurant_info.csv`

Comma-separated file containing information about restaurants in Cambridge. Note that the 'quality'
column was newly added. The specific values for the food quality in this column are purely guesses 
based on the restaurant names. 

### `data/setting.json`

Settings file that can be changed either directly or via `main.py`. Specified settings will change
certain aspects of how the system works.

### `data/vectors.pkl`

Crucial Pickle file that contains word embeddings for the words in the test and training sets.
ONLY delete this file if you have a word embedding vector file such as `fasttext_English.vec` in the `data` folder, and be
prepared to wait a long time the next time you run `mlp.py` or `main.py`.

### `data/wrong_answers_decision_tree.txt`

Text file containing sentences that were wrongly classified by the decision tree.
For each sentence, the predicted label and the actual label are reported.

### `data/wrong_answers_mlp.txt`

Text file containing sentences that were wrongly classified by the multilayer perceptron.
For each sentence, the predicted label and the actual label are reported.
