
import re

import spotlight


class EnglishQuestionParser():
    """
    Poor-man's english question parser. Not even close to conclusive, but
    appears to construct some decent w|a queries and responses.
    
    __author__ = 'seanfitz'
    
    """


    def __init__(self):
        self.regexes = [
            #re.compile(
            #    ".*(?P<QuestionWord>are) "
            #    "(?P<Query>.*)"),
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|whose) "
                "(?P<Query1>.*) (?P<QuestionVerb>is|are|was|were) "
                "(?P<Query2>.*)"),
            re.compile(
                ".*(?P<QuestionWord>are|is) "
                "(?P<Query1>.*) (?P<QuestionVerb>an|a|an example off|an instance off) "
                "(?P<Query2>.*)"),
            re.compile(
                "(?P<Query1>.*) (?P<QuestionVerb>and) "
                "(?P<Query2>.*) (?P<QuestionWord>in common)"),
            re.compile(
                ".*(?P<QuestionWord>talk|rant) "
                "(?P<QuestionVerb>\w+) (?P<Query>.*)"),
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|how|give examples|examples of) "
                "(?P<QuestionVerb>\w+) (?P<Query>.*)")
        ]

    def _normalize(self, groupdict):
        if 'Query' in groupdict:
            return groupdict
        elif 'Query1' and 'Query2' in groupdict:
            return {
                'QuestionWord': groupdict.get('QuestionWord'),
                'QuestionVerb': groupdict.get('QuestionVerb'),
                'Query': ' '.join([groupdict.get('Query1'), groupdict.get(
                    'Query2')])
            }

    def parse(self, utterance):
        for regex in self.regexes:
            match = regex.match(utterance)
            if match:
                return self._normalize(match.groupdict())
        return None


class LILACSQuestionParser():
    def __init__(self):
        self.parser = EnglishQuestionParser()
        self.host = "http://spotlight.sztaki.hu:2222/rest/annotate"

    def process_entitys(self, text):

        subjects, parents, synonims = self.tag_from_dbpedia(text)
        center = 666
        center_node = ""
        for node in subjects:
            if subjects[node] < center:
                center = subjects[node]
                center_node = node

        target = 666
        #TODO better select target mechanism
        target_node = ""
        for node in subjects:
            if subjects[node] < target and node != center_node:
                target = subjects[node]
                target_node = node

        parse = self.poor_parse(text)
        try:
            question = parse["QuestionWord"]
        except:
            question = "unknown"
        middle = [node for node in subjects if node != center_node and node != target_node]
        return center_node, target_node, parents, synonims, middle, question

    def poor_parse(self, text):
        return self.parser.parse(text)

    def tag_from_dbpedia(self, text):
        text = text.lower()
        subjects = {}
        parents = {}
        synonims = {}
        try:
            annotations = spotlight.annotate(self.host, text)
            for annotation in annotations:

                # how sure we are this is about this dbpedia entry
                score = annotation["similarityScore"]
                # entry we are talking about
                subject = annotation["surfaceForm"].lower()
                # smaller is closer to be main topic of sentence
                offset = annotation["offset"]
                # TODO tweak this value and make configuable
                if float(score) < 0.4:
                    continue
                subjects.setdefault(subject, offset)
                # categorie of this <- linked nodes <- parsing for dbpedia search
                if annotation["types"]:
                    p = []
                    types = annotation["types"].split(",")
                    for type in types:
                        type = type.replace("DBpedia:", "").replace("Schema:", "").replace("Http://xmlns.com/foaf/0.1/", "").lower()
                        if type not in p:
                            p.append(type)
                    parents.setdefault(subject, p)
                # dbpedia link
                url = annotation["URI"]
                #print "link: " + url
                dbpedia_name = url.replace("http://dbpedia.org/resource/", "").replace("_", " ")
                if dbpedia_name.lower() not in subject:
                    synonims.setdefault(subject, dbpedia_name.lower())
        except:
            pass
        return subjects, parents, synonims


def test_qp():
    parser = LILACSQuestionParser()

    questions = ["how to kill animals ( a cow ) and make meat", "what is a living being", "why are humans living beings", "give examples of animals"]

    for text in questions:
        center_node, target_node, parents, synonims, midle, question = parser.process_entitys(text)
        print "\nQuestion: " + text
        print "question_type: " + question
        print "center_node: " + center_node
        print "target_node: " + target_node
        print "parents: " + str(parents)
        print "relevant_nodes: " + str(midle)
        print "synonims: " + str(synonims)

if __name__ == '__main__':
	test_qp()