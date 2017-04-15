
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.skills.intent_parser import IntentParser, IntentTree

from mycroft.skills.LILACS.concept import ConceptConnector, ConceptCrawler
from mycroft.skills.knowledgeservice import KnowledgeService
from mycroft.skills.question_parser import EnglishQuestionParser

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
        self.speak("Testing wikipedia backend")
        self.service.adquire("pig", "wikipedia")
        sleep(5)
        self.speak("Testing wikidata backend")
        self.service.adquire("Johnny Cash", "wikidata")
        sleep(5)
        self.speak("Testing wikihow backend")
        self.service.adquire("buy bitcoin", "wikihow")
        sleep(15)
        self.speak("Testing dbpedia backend")
        self.service.adquire("animals", "dbpedia")
        sleep(5)

    def handle_talk_intent(self, message):
        start = random.choice(self.knowledge.get_concept_names())

        for node in self.what_is_this(start):
            if node != start:
                txt = start + " is " + node
                self.speak(txt)

        for node in self.examples_of_this(start):
            if node != start:
                txt = start + " can be " + node
                self.speak(txt)

    def handle_examples_intent(self, message):
        key = random.choice(self.knowledge.get_concept_names())
        examples = self.examples_of_this(key)
        for example in examples:
            if example != key:
                self.speak(example + " is an example of " + key)
        if not examples:
            self.speak("i dont know any examples of " + key)

    def handle_compare_intent(self, message):
        start = random.choice(self.knowledge.get_concept_names())
        target = random.choice(self.knowledge.get_concept_names())
        flag = self.is_this_that(start, target)
        self.speak("answer to is " + start + " a " + target + " is " + str(flag))

    def handle_common_intent(self, message):
        start = random.choice(self.knowledge.get_concept_names())
        target = random.choice(self.knowledge.get_concept_names())
        # what do they have in common
        commons = self.common_this_and_that(start, target)
        for common in commons:
            self.speak(start + " are " + common + " like " + target)

    def handle_relation_intent(self, message):
        start = random.choice(self.knowledge.get_concept_names())
        target = random.choice(self.knowledge.get_concept_names())
        flag = self.is_this_that(start, target)
        self.speak("answer to is " + start + " a " + target + " is " + str(flag))
        if flag:
            # what is relationship
            nodes = self.why_is_this_that(start, target)
            i = 0
            for node in nodes:
                if node != target:
                    self.speak(node + " is " + nodes[i+1])
                i += 1
        else:
            # what do they have in common
            commons = self.common_this_and_that(start, target)
            for common in commons:
                self.speak(start + " are " + common + " like " + target)
            if not commons:
                self.speak("I think they don't have anything in common")

    # LILACS helper

    def why_is_this_that(self, this, that, crawler=None):
        if crawler is None:
            crawler = self.crawler
        crawler.explorer_crawl(this, that)
        nodes = crawler.crawl_path
        return nodes

    def is_this_that(self, this, that, crawler=None):
        if crawler is None:
            crawler = self.crawler
        flag = crawler.drunk_crawl(this, that)
        return flag

    def examples_of_this(self, this, crawler=None):
        if crawler is None:
            crawler = self.crawler
        crawler.drunk_crawl(this, "no target crawl", direction="childs")
        examples = []
        for example in crawler.crawled:
            if example != this:
                examples.append(example)
        return examples

    def common_this_and_that(self, this, that, crawler=None):
        if crawler is None:
            crawler = self.crawler
        crawler.drunk_crawl(this, "no target crawl")
        p_crawl = crawler.crawled
        common = []
        for node in p_crawl:
            flag = crawler.drunk_crawl(that, node)
            if flag:
                common.append(node)
        return common

    def what_is_this(self, this, crawler=None):
        if crawler is None:
            crawler = self.crawler
        crawler.drunk_crawl(this, "no target crawl", direction="parents")
        examples = []
        for example in crawler.crawled:
            examples.append(example)
        return examples

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
