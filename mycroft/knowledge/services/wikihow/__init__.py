from mycroft.knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class WikiHowService(KnowledgeBackend):
    def __init__(self, config, emitter, name='wikihow'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('WikihowKnowledgeAdquire', self._adquire)

    def _adquire(self, message=None):
        logger.info('WikihowKnowledge_Adquire')
        subject = message.data["subject"]
        if subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            how_to = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                links = self.search_wikihow(subject)

                if links == []:
                    logger.error("No wikihow results")
                    return

                for link in links:
                    title = self.get_title(link)
                    steps = self.get_steps(link)
                    how_to[title] = steps
                    logger.info("how to " + title + " : " + str(steps))
                # id info source
                dict["wikihow"] = how_to
                self.emit_node_info(dict)
            except:
                logger.error("Could not parse wikihow for " + str(subject))


    def get_title(self, link):
        # TODO get title of this how-to
        logger.info("Getting title of " + link)
        title = ""
        return title

    def search_wikihow(self, search_term):
        logger.info("Seaching wikihow for " + search_term)
        # TODO get link and title of evey search result
        list = []
        return list

    def get_steps(self, url):
        # TODO get step, and extended description
        steps = {}
        return steps

    def adquire(self, subject):
        logger.info('Call WikihowKnowledgeAdquire')
        self.emitter.emit(Message('WikihowKnowledgeAdquire', {"subject": subject}))

    def emit_node_info(self, info):
        # TODO emit node_info for node manager to update/create node
        for source in info:
            for key in info[source]:
                print "\n" + key + " : " + str(info[source][key])

    def stop(self):
        logger.info('WikihowKnowledge_Stop')
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wikihow']
    instances = [WikiHowService(s[1], emitter, s[0]) for s in services]
    return instances
