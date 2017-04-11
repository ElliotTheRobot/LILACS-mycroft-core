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
        self.subject = None
        self.emitter.on('WikidataKnowledgeAdquire', self._adquire)

    def set_subject(self, subject):
        self.subject = subject

    def _adquire(self, message=None):
        logger.info('WikidataKnowledge_Adquire')
        if self.subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            node_data = {}
            subject = self.subject
            # get knowledge about
            # TODO exception handling for erros
            try:
                page = wptools.page(subject).get_wikidata()
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
                self.emit_node_info(dict)
            except:
                logger.error("Could not parse wikidata for " + str(subject))

    def adquire(self):
        logger.info('Call WikidataKnowledgeAdquire')
        self.emitter.emit(Message('WikidataKnowledgeAdquire'))

    def emit_node_info(self, info):
        # TODO emit node_info for node manager to update/create node
        for source in info:
            print source
            for key in source:
                print key + " : " + str(source[key])

    def stop(self):
        logger.info('WikidataKnowledge_Stop')
        self.subject = None
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wikidata']
    instances = [WikidataService(s[1], emitter, s[0]) for s in services]
    return instances
