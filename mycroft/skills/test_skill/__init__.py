
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.skills.intent_parser import IntentParser, IntentTree

from mycroft.skills.LILACS_core.concept import ConceptConnector, ConceptCrawler
from mycroft.skills.knowledgeservice import KnowledgeService
from mycroft.skills.question_parser import EnglishQuestionParser
from mycroft.skills.LILACS_core.questions import *

import random
from time import sleep

__author__ = 'jarbas'

logger = getLogger(__name__)


class TestSkill(MycroftSkill):

    def __init__(self):
        super(TestSkill, self).__init__(name="TestSkill")
        # concept connector
        self.knowledge = ConceptConnector()
        self.crawler = None
        self.service = None
        self.question_parser = EnglishQuestionParser


    def initialize(self):
        # initialize self intent parser
        self.intent_parser = IntentParser(self.emitter)
        # register intents
        self.build_intents()
        # make tree
        # self.build_intent_tree()
        # create concepts
        self.create_concepts()
        # initialize crawler
        self.crawler = ConceptCrawler(concept_connector=self.knowledge)
        # initialize knowledge service
        self.service = KnowledgeService(self.emitter)
        # register messagebus signals
        # self.register_signals()

   # def register_signals(self):
   #     self.emitter.on("WikipediaKnowledgeResult", self.end_wait)
   #     self.emitter.on("WikidataKnowledgeResult", self.end_wait)
   #     self.emitter.on("WikihowKnowledgeResult", self.end_wait)
   #     self.emitter.on("DBPediaKnowledgeResult", self.end_wait)

    def build_intents(self):
        # build
        examples_intent = IntentBuilder("GiveExamplesIntent") \
            .require("ExamplesKeyword").build()
        common_intent = IntentBuilder("CommonThingsIntent") \
            .require("CommonKeyword").build()
        compare_intent = IntentBuilder("CompareThingsIntent") \
            .require("CompareKeyword").build()
        relation_intent = IntentBuilder("ShortestPathIntent") \
            .require("RelationKeyword").build()
        talk_intent = IntentBuilder("TalkAboutIntent") \
            .require("TalkKeyword").build()
        test_intent = IntentBuilder("TestKnowledgeIntent") \
            .require("TestKeyword").build()

        # register intents
        self.register_intent(examples_intent,
                             self.handle_examples_intent)
        self.register_intent(common_intent,
                             self.handle_common_intent)
        self.register_intent(compare_intent,
                             self.handle_compare_intent)
        self.register_intent(relation_intent,
                             self.handle_relation_intent)
        self.register_intent(talk_intent,
                             self.handle_talk_intent)
        self.register_intent(test_intent,
                             self.handle_test_knowledge_backend_intent)

    def build_intent_tree(self):
        pass

    def create_concepts(self):
        # create concepts for testing
        name = "human"
        child_concepts = {"human_male": 1, "human_female": 1}
        parent_concepts = {"animal": 2, "mammal": 1}
        self.knowledge.create_concept(name, parent_concepts=parent_concepts,
                                 child_concepts=child_concepts)

        name = "joana"
        child_concepts = {"human_wife": 1}
        parent_concepts = {"human_female": 2, "human": 1}
        self.knowledge.create_concept(name, parent_concepts=parent_concepts,
                                 child_concepts=child_concepts)

        name = "maria"
        child_concepts = {"human_wife": 1}
        parent_concepts = {"human_female": 2, "human": 1}
        self.knowledge.create_concept(name, parent_concepts=parent_concepts,
                                 child_concepts=child_concepts)

        name = "animal"
        child_concepts = {"dog": 2, "cow": 2, "frog": 2, "cat": 2, "spider": 2, "insect": 1, "mammal": 1}
        parent_concepts = {"living being": 1}
        self.knowledge.create_concept(name, parent_concepts=parent_concepts,
                                 child_concepts=child_concepts)

    def handle_test_knowledge_backend_intent(self, message):

        subj = "human"
        backend = "wordnik"

        self.speak("Testing " + backend + " backend")

        result = self.service.adquire(subj, backend)
        if result == {}:
            self.speak("could not get any data for " + backend)
        else:
            for key in result[backend]:
                self.speak(key + " is " + str(result[backend][key]))

    def handle_talk_intent(self, message):
        start = random.choice(self.knowledge.get_concept_names())

        for node in what_is_this(start):
            if node != start:
                txt = start + " is " + node
                self.speak(txt)

        for node in examples_of_this(start):
            if node != start:
                txt = start + " can be " + node
                self.speak(txt)

    def handle_examples_intent(self, message):
        key = random.choice(self.knowledge.get_concept_names())
        examples = examples_of_this(key)
        for example in examples:
            if example != key:
                self.speak(example + " is an example of " + key)
        if not examples:
            self.speak("i dont know any examples of " + key)

    def handle_compare_intent(self, message):
        start = random.choice(self.knowledge.get_concept_names())
        target = random.choice(self.knowledge.get_concept_names())
        flag = is_this_that(start, target)
        self.speak("answer to is " + start + " a " + target + " is " + str(flag))

    def handle_common_intent(self, message):
        start = random.choice(self.knowledge.get_concept_names())
        target = random.choice(self.knowledge.get_concept_names())
        # what do they have in common
        commons = common_this_and_that(start, target)
        for common in commons:
            self.speak(start + " are " + common + " like " + target)

    def handle_relation_intent(self, message):
        start = random.choice(self.knowledge.get_concept_names())
        target = random.choice(self.knowledge.get_concept_names())
        flag = is_this_that(start, target)
        self.speak("answer to is " + start + " a " + target + " is " + str(flag))
        if flag:
            # what is relationship
            nodes = why_is_this_that(start, target)
            i = 0
            for node in nodes:
                if node != target:
                    self.speak(node + " is " + nodes[i+1])
                i += 1
        else:
            # what do they have in common
            commons = common_this_and_that(start, target)
            for common in commons:
                self.speak(start + " are " + common + " like " + target)
            if not commons:
                self.speak("I think they don't have anything in common")

    # standard methods
    
    def stop(self):
        pass

    def converse(self, transcript, lang="en-us"):
        # tell intent skill if you handled intent
        return False

    def feedback(self, feedback, lang):
        if feedback == "positive":
            # do stuff on positive reinforcement words intent
            pass
        elif feedback == "negative":
            # do stuff on negative reinforcement words inten
            pass


def create_skill():
    return TestSkill()
