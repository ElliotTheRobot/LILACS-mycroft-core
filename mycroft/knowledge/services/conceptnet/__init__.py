from mycroft.knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

import requests

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class ConceptNetService(KnowledgeBackend):
    def __init__(self, config, emitter, name='conceptnet'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('ConceptNetKnowledgeAdquire', self._adquire)

    def _adquire(self, message=None):
        logger.info('ConceptNetKnowledge_Adquire')
        subject = message.data["subject"]
        if subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                parents = []
                capable = []
                has = []
                desires = []
                used = []
                related = []
                examples = []
                location = []

                obj = requests.get('http://api.conceptnet.io/c/en/' + subject).json()
                for edge in obj["edges"]:
                    rel = edge["rel"]["label"]
                    node = edge["end"]["label"]
                    if rel == "IsA":
                        node = node.replace("a ", "").replace("an ", "")
                        if node not in parents:
                            parents.append(node)
                    elif rel == "CapableOf":
                        if node not in capable:
                            capable.append(node)
                    elif rel == "HasA":
                        if node not in has:
                            has.append(node)
                    elif rel == "Desires":
                        if node not in desires:
                            desires.append(node)
                    elif rel == "UsedFor":
                        if node not in used:
                            used.append(node)
                    elif rel == "RelatedTo":
                        if node not in related:
                            related.append(node)
                    elif rel == "AtLocation":
                        if node not in location:
                            location.append(node)
                    usage = edge["surfaceText"]
                    if usage is not None:
                        examples.append(usage)
                # id info source
                dict.setdefault("conceptnet", {"IsA":parents, "CapableOf":capable, "HasA":has, "Desires":desires, "UsedFor":used, "RelatedTo":related, "AtLocation":location, "surfaceText":examples})
                self.emit_node_info(dict)
            except:
                logger.error("Could not parse conceptnet for " + str(subject))


    def adquire(self, subject):
        logger.info('Call ConceptNetKnowledgeAdquire')
        self.emitter.emit(Message('ConceptNetKnowledgeAdquire', {"subject": subject}))

    def emit_node_info(self, info):
        # TODO emit node_info for node manager to update/create node
        for source in info:
            for key in info[source]:
                print "\n" + key + " : " + str(info[source][key])
        self.emitter.emit(Message('ConceptNetKnowledgeResult', {"conceptnet": info}))

    def stop(self):
        logger.info('ConceptNetKnowledge_Stop')
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'conceptnet']
    instances = [ConceptNetService(s[1], emitter, s[0]) for s in services]
    return instances
