from mycroft.knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

import wptools

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class WikipediaService(KnowledgeBackend):
    def __init__(self, config, emitter, name='wikipedia'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('WikipediaKnowledgeAdquire', self._adquire)

    def _adquire(self, message=None):
        logger.info('WikipediaKnowledge_Adquire')
        subject = message.data["subject"]
        if subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            node_data = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                page = wptools.page(subject, silent=True, verbose=False).get_query()
                node_data["pic"] = page.image('page')['url']
                node_data["name"] = page.label
                node_data["description"] = page.description
                node_data["summary"] = page.extext
                node_data["url"] = page.url
                # parse infobox
                node_data["infobox"] = self.parse_infobox(subject)
                # id info source
                dict["wikipedia"] = node_data

            except:
                logger.error("Could not parse wikipedia for " + str(subject))
            self.send_result(dict)

    def parse_infobox(self, subject):
        page = wptools.page(subject, silent=True, verbose=False).get_parse()
        data = {}
        # TODO decent parsing, info is messy
        for entry in page.infobox:
            #print entry + " : " + page.infobox[entry]
            data[entry] = page.infobox[entry]

        return data


    def adquire(self, subject):
        logger.info('Call WikipediaKnowledgeAdquire')
        self.emitter.emit(Message('WikipediaKnowledgeAdquire', {"subject": subject}))

    def send_result(self, result = {}):
        self.emitter.emit(Message("LILACS_result", {"data": result}))

    def stop(self):
        logger.info('WikipediaKnowledge_Stop')
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wikipedia']
    instances = [WikipediaService(s[1], emitter, s[0]) for s in services]
    return instances
