
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
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|whose) "
                "(?P<Query1>.*) (?P<QuestionVerb>is|are|was|were) "
                "(?P<Query2>.*)"),
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|how|give examples) "
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

        subjects, parents = self.tag_from_dbpedia(text)

        center = 666
        center_node = ""
        for node in subjects:
            if subjects[node] < center:
                center = subjects[node]
                center_node = node

        target = 666
        target_node = ""
        for node in subjects:
            if subjects[node] < target and node != center_node:
                target = subjects[node]
                target_node = node

        parse = self.poor_parse(text)
        question = parse["QuestionWord"]

        return center_node, target_node, parents, question

    def poor_parse(self, text):
        return self.parser.parse(text)

    def tag_from_dbpedia(self, text):
        annotations = spotlight.annotate(self.host, text)
        subjects = {}
        parents = []
        for annotation in annotations:
            # how sure we are this is about this dbpedia entry
            score = annotation["similarityScore"]
            #print "\nscore : " + str(score)
            # entry we are talking about
            subject = annotation["surfaceForm"]
            #print "subject: " + subject
            # smaller is closer to be main topic of sentence
            offset = annotation["offset"]
            #print "offset: " + str(offset)
            if float(score) < 0.4:
                continue
            subjects.setdefault(subject, offset)
            # categorie of this <- linked nodes <- parsing for dbpedia search
            if annotation["types"]:
                types = annotation["types"].split(",")
                for type in types:
                    #print "type: " + type
                    parents.append(type.replace("DBpedia:",""))
            # dbpedia link
           # url = annotation["URI"]
            #print "link: " + url

        return subjects, parents



parser = LILACSQuestionParser()
text = "how to kill a chicken"
print "\nQuestion: " + text
center_node, target_node, parents, question = parser.process_entitys(text)
print "center_node: " + center_node
print "target_node: " + target_node
print "parents: " + str(parents)
print "question_type: " + question


text = "what is a frog"
print "\nQuestion: " + text
center_node, target_node, parents, question = parser.process_entitys(text)
print "center_node: " + center_node
print "target_node: " + target_node
print "parents: " + str(parents)
print "question_type: " + question

text = "why are humans living beings"
print "\nQuestion: " + text
center_node, target_node, parents, question = parser.process_entitys(text)
print "center_node: " + center_node
print "target_node: " + target_node
print "parents: " + str(parents)
print "question_type: " + question

text = "give examples of animals"
print "\nQuestion: " + text
center_node, target_node, parents, question = parser.process_entitys(text)
print "center_node: " + center_node
print "target_node: " + target_node
print "parents: " + str(parents)
print "question_type: " + question