from abc import ABC, abstractmethod 
  
class abstract_machine_learning_algorithm(ABC): 

    # abstract method 
    def perform_algorithm(self, decision_type): 
        pass

    def predict(self, input_sentence, model, scaler, id_to_label, pickle_file):
        pass