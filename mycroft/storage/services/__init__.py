from abc import ABCMeta, abstractmethod

__author__ = 'jarbas'


# add here all methods all backends are expected to implement

class StorageBackend():
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, config, emitter):
        pass

    @abstractmethod
    def save(self, node):
        pass

    @abstractmethod
    def load(self, node):
        pass

    @abstractmethod
    def stop(self):
        pass
