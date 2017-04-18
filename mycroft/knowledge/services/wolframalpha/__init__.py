import re
from os.path import abspath

import wolframalpha
from mycroft.skills.question_parser import LILACSQuestionParser
from requests import HTTPError

from mycroft.configuration import ConfigurationManager
from mycroft.knowledge.services import KnowledgeBackend
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger

PIDS = ['Value', 'NotableFacts:PeopleData', 'BasicInformation:PeopleData',
        'Definition', 'DecimalApproximation']

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class WolframAlpha(KnowledgeBackend):
    def __init__(self, config, emitter, name='wolfram alpha'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('WolframAlphaKnowledgeAdquire', self._adquire)
        self.api = ConfigurationManager.get().get("WolframAlphaSkill").get("api_key")
        self.client = wolframalpha.Client(self.api)
        self.parser = LILACSQuestionParser()

    def _adquire(self, message=None):
        logger.info('WolframAlphaKnowledge_Adquire')
        subject = message.data["subject"]
        if subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                response, parents, synonims, midle = self.wolfram_to_nodes(subject)
                node_data = {"answer":response, "parents":parents, "synonims":synonims, "relevant":midle}
                # id info source
                dict["wolfram alpha"] = node_data
            except:
                logger.error("Could not parse wolfram alpha for " + str(subject))
            self.send_result(dict)


    def adquire(self, subject):
        logger.info('Call WolframKnowledgeAdquire')
        self.emitter.emit(Message('WolframAlphaKnowledgeAdquire', {"subject": subject}))

    def send_result(self, result={}):
        self.emitter.emit(Message("LILACS_result", {"data": result}))


    def wolfram_to_nodes(self, query, lang="en-us"):

        responses = self.ask_wolfram(query)
        txt = query.lower().replace("the ", "").replace("an ", "").replace("a ", "")
        center_node, target_node, parents, synonims, midle, question = self.parser.process_entitys(txt)

        response = responses[0]

        txt = response.lower().replace("the ", "").replace("an ", "").replace("a ", "")
        if txt != "no answer":
            midle2, parents2, synonims2 = self.parser.tag_from_dbpedia(txt)

            for parent in parents2:
                if parent not in parents:
                    parents.setdefault(parent, parents2[parent])
            midle += midle2
            for synonim in synonims2:
                synonims.setdefault(synonim, synonims2[synonim])

        return response, parents, synonims, midle

    def get_result(self, res):
        try:
            return next(res.results).text
        except:
            result = None
            try:
                for pid in PIDS:
                    result = self.__find_pod_id(res.pods, pid)
                    if result:
                        result = result[:5]
                        break
                if not result:
                    result = self.__find_num(res.pods, '200')
                return result
            except:
                return result

    def __find_pod_id(self, pods, pod_id):
        for pod in pods:
            if pod_id in pod.id:
                return pod.text
        return None

    def __find_num(self, pods, pod_num):
        for pod in pods:
            if pod.node.attrib['position'] == pod_num:
                return pod.text
        return None

    def _find_did_you_mean(self, res):
        value = []
        root = res.tree.find('didyoumeans')
        if root is not None:
            for result in root:
                value.append(result.text)
        return value

    def process_wolfram_string(self, text, lang):
        # Remove extra whitespace
        text = re.sub(r" \s+", r" ", text)

        # Convert | symbols to commas
        text = re.sub(r" \| ", r", ", text)

        # Convert newlines to commas
        text = re.sub(r"\n", r", ", text)

        # Convert !s to factorial
        text = re.sub(r"!", r",factorial", text)

        regex = "(1,|1\.) (?P<Definition>.*) (2,|2\.) (.*)"
        list_regex = re.compile(regex)

        match = list_regex.match(text)
        if match:
            text = match.group('Definition')

        return text

    def ask_wolfram(self, query, lang="en-us"):
        others = []
        result = None
        try:
            res = self.client.query(query)
            result = self.get_result(res)
            if result is None:
                others = self._find_did_you_mean(res)
        except HTTPError as e:
            print "mycroft.not.paired"
        except:
            print "error"

        response = ["no answer"]
        if result:
            input_interpretation = self.__find_pod_id(res.pods, 'Input')
            verb = "is"

            if "|" in result:  # Assuming "|" indicates a list of items
                verb = ":"

            result = self.process_wolfram_string(result, lang)
            input_interpretation = \
                self.process_wolfram_string(input_interpretation, lang)
            response = "%s %s %s" % (input_interpretation, verb, result)
            i = response.find("?")
            if i != -1:
                response = response[i + 1:].replace("is ", "").replace("(", "\n").replace(")", " ")
            response = [response]

        else:
            if len(others) > 0:
                for other in others:
                    response.append(self.ask_wolfram(other))

        return response

    def stop(self):
        logger.info('WolframAlphaKnowledge_Stop')
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wolfram alpha']
    instances = [WolframAlpha(s[1], emitter, s[0]) for s in services]
    return instances
