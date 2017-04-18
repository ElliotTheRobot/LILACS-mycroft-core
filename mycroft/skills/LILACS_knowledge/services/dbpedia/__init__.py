import json
from os.path import abspath

import spotlight
import urlfetch

from mycroft.messagebus.message import Message
from mycroft.skills.LILACS_knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger

# TODO read this from config
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
                    node["parents"] = types
                    # dbpedia link
                    url = annotation["URI"]
                    node["url"] = url
                    node["page_info"] = self.scrap_resource_page(url)
                    node_data[subject] = node

                # id info source
                dict["dbpedia"] = node_data
            except:
                logger.error("Could not parse dbpedia for " + str(subject))
            self.send_result(dict)

    def scrap_resource_page(self, link):
        u = link.replace("http://dbpedia.org/resource/", "http://dbpedia.org/data/") + ".json"
        data = urlfetch.fetch(url=u)
        json_data = json.loads(data.content)
        dbpedia = {}
        dbpedia["related_subjects"] = []
        dbpedia["picture"] = []
        dbpedia["external_links"] = []
        dbpedia["abstract"] = ""
        for j in json_data[link]:
            if "#seeAlso" in j:
                # complimentary nodes
                for entry in json_data[link][j]:
                    value = entry["value"].replace("http://dbpedia.org/resource/", "").replace("_", " ").encode("utf8")
                    if value not in dbpedia["related_subjects"]:
                        dbpedia["related_subjects"].append(value)
            elif "wikiPageExternalLink" in j:
                # links about this subject
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    dbpedia["external_links"].append(value)
            elif "subject" in j:
                # relevant nodes
                for entry in json_data[link][j]:
                    value = entry["value"].replace("http://dbpedia.org/resource/Category:", "").replace("_", " ").encode("utf8")
                    if value not in dbpedia["related_subjects"]:
                        dbpedia["related_subjects"].append(value)
            elif "abstract" in j:
                # english description
                dbpedia["abstract"] = \
                    [abstract['value'] for abstract in json_data[link][j] if abstract['lang'] == 'en'][0].encode("utf8")
            elif "depiction" in j:
                # pictures
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    dbpedia["picture"].append(value)
            elif "isPrimaryTopicOf" in j:
                # usually original wikipedia link
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    # dbpedia["primary"].append(value)
            elif "wasDerivedFrom" in j:
                # usually wikipedia link at scrap date
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    # dbpedia["derived_from"].append(value)
            elif "owl#sameAs" in j:
                # links to dbpedia in other languages
                for entry in json_data[link][j]:
                    value = entry["value"].encode("utf8")
                    if "resource" in value:
                        # dbpedia["same_as"].append(value)
                        pass

        return dbpedia

    def adquire(self, subject):
        logger.info('Call DBpediaKnowledgeAdquire')
        self.emitter.emit(Message('DBpediaKnowledgeAdquire', {"subject": subject}))

    def send_result(self, result = {}):
        self.emitter.emit(Message("LILACS_result", {"data": result}))

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
