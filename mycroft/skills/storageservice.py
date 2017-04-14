from mycroft.messagebus.message import Message


class StorageService():
    def __init__(self, emitter):
        self.emitter = emitter

    def load(self, node="consciousness", utterance=''):
        self.emitter.emit(Message('LILACS_StorageService_load',
                                  data={'node': node,
                                        'utterance': utterance}))

    def save(self, node="consciousness", utterance=''):
        self.emitter.emit(Message('LILACS_StorageService_save',
                                  data={'node': node,
                                        'utterance': utterance}))

