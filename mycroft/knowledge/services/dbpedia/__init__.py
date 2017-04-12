from mycroft.knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

import spotlight

host = "http://spotlight.sztaki.hu:2222/rest/annotate"

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class DBpediaService(KnowledgeBackend):
    def __init__(self, config, emitter, name='dbpedia'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('DBpediaKnowledgeAdquire', self._adquire)

    def _adquire(self, message=None):
        logger.info('DBpediaKnowledge_Adquire')
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
                text = subject
                annotations = spotlight.annotate(host, text)
                for annotation in annotations:
                    node = {}
                    # how sure we are this is about this dbpedia entry
                    score = annotation["similarityScore"]
                    node["score"] = score
                    # entry we are talking about
                    subject = annotation["surfaceForm"]
                    node["subject"] = subject
                    # smaller is closer to be main topic of sentence
                    offset = annotation["offset"]
                    node["offset"] = offset
                    # categorie of this <- linked nodes <- parsing for dbpedia search
                    types = annotation["types"].split(",")
                    node["types"] = types
                    # dbpedia link
                    url = annotation["URI"]
                    node["url"] = url

                    node_data[subject] = node

                # id info source
                dict["dbpedia"] = node_data
                self.emit_node_info(dict)
            except:
                logger.error("Could not parse dbpedia for " + str(subject))


    def adquire(self, subject):
        logger.info('Call DBpediaKnowledgeAdquire')
        self.emitter.emit(Message('DBpediaKnowledgeAdquire', {"subject": subject}))

    def emit_node_info(self, info):
        # TODO emit node_info for node manager to update/create node
        for source in info:
            for key in info[source]:
                print "\n" + key + " : " + str(info[source][key])

    def stop(self):
        logger.info('DBpediaKnowledge_Stop')
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'dbpedia']
    instances = [DBpediaService(s[1], emitter, s[0]) for s in services]
    return instances
