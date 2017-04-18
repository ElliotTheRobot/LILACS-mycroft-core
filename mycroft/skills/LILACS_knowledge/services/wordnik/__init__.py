from os.path import abspath

from mycroft.messagebus.message import Message
from mycroft.skills.LILACS_knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from wordnik import *

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class Wordnik(KnowledgeBackend):
    def __init__(self, config, emitter, name='word nik'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('WordnikKnowledgeAdquire', self._adquire)
        apiUrl = 'http://api.wordnik.com/v4'
        # TODO read from config
        apiKey = "39f2ba7ddaef2fe609301073d1e014ba34ecfb7574a20e83c"
        client = swagger.ApiClient(apiKey, apiUrl)
        self.wordApi = WordApi.WordApi(client)
        self.limit = 5



    def _adquire(self, message=None):
        logger.info('WordnikKnowledge_Adquire')
        subject = message.data["subject"]
        if subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                node_data = {}
                node_data["relations"] = self.get_related_words(subject)
                node_data["definitions"] = self.get_definitions(subject)
                # id info source
                dict["wordnik"] = node_data
            except:
                logger.error("Could not parse wordnik for " + str(subject))
            self.send_result(dict)


    def adquire(self, subject):
        logger.info('Call WordnikAdquire')
        self.emitter.emit(Message('WordnikKnowledgeAdquire', {"subject": subject}))

    def send_result(self, result={}):
        self.emitter.emit(Message("LILACS_result", {"data": result}))

    def get_definitions(self, subject):
        definitions = self.wordApi.getDefinitions(subject,
                                             partOfSpeech='noun',
                                             sourceDictionaries='all',
                                             limit=self.limit)
        defs = []
        try:
            for defi in definitions:
                defs.append(defi.text)
        except:
            pass
        return defs

    def get_related_words(self, subject):
        res = self.wordApi.getRelatedWords(subject)
        words = {}
        try:
            for r in res:
                words.setdefault(r.relationshipType, r.words)
        except:
            pass
        return words


    def stop(self):
        logger.info('WordnikKnowledge_Stop')
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wordnik']
    instances = [Wordnik(s[1], emitter, s[0]) for s in services]
    return instances
