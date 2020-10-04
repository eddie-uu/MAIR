# MAIR RestRec
This project implements a restaurant recommendation system based on both labeled 
user queries and a database of restaurants in Cambridge. The system works as a 
command line program, where the user can type in queries and interact with the 
system in different ways.

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

You will also need SWI Prolog version 7.2 or higher installed.

All testing of this code has been on Windows 10, no guarantees for other operating systems/versions.

## Start
In order to start the application, navigate to the main directory of this project 
and type the following command in your console to start the execution:

`python main.py`

At first, you will be presented with 8 different options. Type the number (1-8) to use 
the system in the corresponding way. See section on `main.py` for more information.

You can view example dialogs with the system in `examples.txt`.

## Files

### `main.py`

### `dialog_flow.py`

### `extract.py`

### `abstract_mla.py`

### `baseline_systems.py`

### `decision_tree.py`

### `mlp.py`

### `extract_info.py`

### `imply.py`

### `keyword_algorithm.py`

### `data/all_dialogs.txt`

Contains all unedited dialogs used for training. Not used in the code, but useful for reference.

### `data/decision_tree.pkl`

Pickle file in order to be able to use a pretrained decision tree model at dialog execution time.
Make sure to delete this file if you change `dialog_acts.dat`.

### `data/dialog_acts.dat`

Preprocessed training data for training the dialog classifiers. First word on a line is the label.

### `data/fasttext_English.vec`

NOT INCLUDED

### `data/implications.pl`

Precomputed Prolog knowledge base used by `implications.py`. Make sure to delete this file if you 
change either `restaurant_info.csv` or `implications.tsv`. Note that you can also query this
knowledge base by consulting this file in Prolog.

### `data/implications.tsv`

Tab-separated file containing reasoning rules used by `implications.py`. Inspection of this file
also provides a description of each rule.

### `data/mlp_model.pkl`

NOT INCLUDED
Pickle file in order to be able to use a pretrained multilayer perceptron model at dialog execution time.
Make sure to delete this file if you change either `dialog_acts.dat` or 
scikit

### `data/restaurant_info.csv`

### `data/setting.json`

### `data/vectors.pkl`

### `data/wrong_answers_decision_tree.txt`

### `data/wrong_answers_mlp.txt`

