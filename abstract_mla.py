from abc import ABC, abstractmethod 
  
class AbstractMachineLearningAlgorithm(ABC): 

    # abstract method 
    def performAlgorithm(self, decisionType): 
        pass