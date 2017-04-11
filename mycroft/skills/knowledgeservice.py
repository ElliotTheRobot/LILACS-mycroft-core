from mycroft.messagebus.message import Message


class KnowledgeService():
    def __init__(self, emitter):
        self.emitter = emitter

    def adquire(self, subject="consciousness", utterance=''):
        self.emitter.emit(Message('LILACS_KnowledgeService_adquire',
                                  data={'subject': subject,
                                        'utterance': utterance}))

