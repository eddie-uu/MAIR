# MAIR Dialog chatbot project
## Setup
### The following libraries need to be installed for succesfull execution of the project:
* Scikit
* Pandas
* Python-Levenshtein
* NLTK
* Numpy
* PYswip
### You will also need SWI Prolog version 7.2 or higher installed.

## Start
Since the application is a console only application, in order to start the application, type the following command in your console to start the project:
python main.py

## State transition diagram
In the following directory is the state diagram available which was used for the first version of the dialog flow:
/data/state_transition_model.pdf

## Note
Not everything is fully connected and/or tested yet at this stage. For example, some options don't change anything.
Most interesting python files to look at this time: imply.py, dialog_flow.py.
Most interesting other files: implications.tsv/pl, extra column in restaurant_info.csv, settings.json.