from abc import ABC, abstractmethod

class AuthBase(ABC):

    # More methods to be added as session auths are worked on

    def __init__(self):
        pass

    @abstractmethod
    def add_arguments(self, options):
        pass