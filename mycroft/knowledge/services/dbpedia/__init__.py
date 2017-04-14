from mycroft.knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

import spotlight
import json
import urlfetch

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
                    node["page_info"] = self.scrap_resource_page(url)
                    node_data[subject] = node

                # id info source
                dict["dbpedia"] = node_data
                self.emit_node_info(dict)
            except:
                logger.error("Could not parse dbpedia for " + str(subject))

    def scrap_resource_page(self, link):
        u = link.replace("http://dbpedia.org/resource/", "http://dbpedia.org/data/") + ".json"
        data = urlfetch.fetch(url=u)
        json_data = json.loads(data.content)
        dbpedia = {}
        for j in json_data[link]:
            if "#seeAlso" in j:
                # complimentary nodes
                dbpedia["see_also"] = []
                for entry in json_data[link][j]:
                    value = entry["value"]
                    dbpedia["see_also"].append(value)
            elif "wikiPageExternalLink" in j:
                # links about this subject
                dbpedia["external_links"] = []
                for entry in json_data[link][j]:
                    value = entry["value"]
                    dbpedia["external_links"].append(value)
            elif "subject" in j:
                # relevant nodes
                dbpedia["related_subjects"] = []
                for entry in json_data[link][j]:
                    value = entry["value"]
                    dbpedia["related_subjects"].append(value)
            elif "abstract" in j:
                # english description
                dbpedia["abstract"] = \
                [abstract['value'] for abstract in json_data[link][j] if abstract['lang'] == 'en'][0]
            elif "depiction" in j:
                # pictures
                dbpedia["picture"] = []
                for entry in json_data[link][j]:
                    value = entry["value"]
                    dbpedia["picture"].append(value)
            elif "isPrimaryTopicOf" in j:
                # usually original wikipedia link
                dbpedia["primary"] = []
                for entry in json_data[link][j]:
                    value = entry["value"]
                    #dbpedia["primary"].append(value)
            elif "wasDerivedFrom" in j:
                # usually wikipedia link at scrap date
                dbpedia["derived_from"] = []
                for entry in json_data[link][j]:
                    value = entry["value"]
                    #dbpedia["derived_from"].append(value)
            elif "owl#sameAs" in j:
                # links to dbpedia in other languages
                dbpedia["same_as"] = []
                for entry in json_data[link][j]:
                    value = entry["value"]
                    if "resource" in value:
                        #dbpedia["same_as"].append(value)
                        pass

        return dbpedia

    def adquire(self, subject):
        logger.info('Call DBpediaKnowledgeAdquire')
        self.emitter.emit(Message('DBpediaKnowledgeAdquire', {"subject": subject}))

    def emit_node_info(self, info):
        # TODO emit node_info for node manager to update/create node
        for source in info:
            for key in info[source]:
                pass
                #print "\n" + key + " : " + str(info[source][key])
        self.emitter.emit(Message('DBPediaResult', {"dbpedia": info}))

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
