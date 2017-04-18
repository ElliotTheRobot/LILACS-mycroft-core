from mycroft.knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

import wptools

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class WikidataService(KnowledgeBackend):
    def __init__(self, config, emitter, name='wikidata'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('WikidataKnowledgeAdquire', self._adquire)


    def _adquire(self, message=None):
        logger.info('WikidataKnowledge_Adquire')
        subject = message.data["subject"]
        if subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            node_data = {}
            # get knowledge about
            # TODO exception handling for erros
            try:
                page = wptools.page(subject, silent=True, verbose=False).get_wikidata()
                # parse for distant child of
                node_data["description"] = page.description
                # direct child of
                node_data["what"] = page.what
                # data fields
                node_data["data"] = page.wikidata
                # related to
                # TODO parse and make cousin/child/parent
                node_data["properties"] = page.props
                # id info source
                dict["wikidata"] = node_data
            except:
                logger.error("Could not parse wikidata for " + str(subject))
            self.send_result(dict)

    def adquire(self, subject):
        logger.info('Call WikidataKnowledgeAdquire')
        self.emitter.emit(Message('WikidataKnowledgeAdquire', {"subject": subject}))

    def send_result(self, result = {}):
        self.emitter.emit(Message("LILACS_result", {"data": result}))

    def stop(self):
        logger.info('WikidataKnowledge_Stop')
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wikidata']
    instances = [WikidataService(s[1], emitter, s[0]) for s in services]
    return instances
