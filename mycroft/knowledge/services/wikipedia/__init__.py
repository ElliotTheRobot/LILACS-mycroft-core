import subprocess
from mycroft.knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class WikipediaService(KnowledgeBackend):
    def __init__(self, config, emitter, name='wikipedia'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.subject = None
        self.emitter.on('WikipediaKnowledgeAdquire', self._adquire)

    def set_subject(self, subject):
        self.subject = subject

    def _adquire(self, message=None):
        logger.info('WikipediaKnowledge_Adquire')
        if self.subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            subject = self.subject
            # get knowledge about

    def adquire(self):
        logger.info('Call WikipediaKnowledgeAdquire')
        self.index = 0
        self.emitter.emit(Message('WikipediaKnowledgeAdquire'))

    def stop(self):
        logger.info('WikipediaKnowledge_Stop')
        self.clear_list()
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wikipedia']
    instances = [WikipediaService(s[1], emitter, s[0]) for s in services]
    return instances
