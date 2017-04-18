from mycroft.messagebus.message import Message


class KnowledgeService():
    def __init__(self, emitter):
        self.emitter = emitter
        self.result = None
        self.emitter.on("LILACS_result", self.get_result)
        self.waiting = False

    def adquire(self, subject="consciousness", utterance=''):
        self.waiting = True
        self.emitter.emit(Message('LILACS_KnowledgeService_adquire',
                                  data={'subject': subject,
                                        'utterance': utterance}))
        while self.waiting:
            pass
        return self.result

    def get_result(self, message):
        self.result = message.data["data"]
        self.waiting = False

