# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

from mycroft.skills.intent_parser import IntentParser, IntentTree

from mycroft.skills.LILACS.concept import ConceptConnector, ConceptCrawler
from mycroft.skills.LILACS.storage import ConceptStorage

__author__ = 'jarbas'

logger = getLogger(__name__)


class TestSkill(MycroftSkill):

    def __init__(self):
        super(TestSkill, self).__init__(name="TestSkill")
        # concept connector
        self.knowledge = ConceptConnector()
        self.crawler=None

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

        # register intents
        self.register_intent(examples_intent,
                             self.handle_examples_intent)
        self.register_intent(common_intent,
                             self.handle_common_intent)
        self.register_intent(compare_intent,
                             self.handle_compare_intent)
        self.register_intent(relation_intent,
                             self.handle_relation_intent)

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
        child_concepts = {"dog": 1, "cow": 1, "frog": 1, "cat": 1, "spider": 1, "insect": 1}
        parent_concepts = {"living being": 1}
        self.knowledge.create_concept(name, parent_concepts=parent_concepts,
                                 child_concepts=child_concepts)
    
    # intent handling
    
    def handle_examples_intent(self, message):
        key = "animal"
        for example in self.examples_of_this(key):
            self.speak(example + " is an example of " + key)

    def handle_compare_intent(self, message):
        start = "maria"
        target = "living being"
        flag = self.is_this_that(start, target)
        self.speak("answer to is " + start + " a " + target + " is " + str(flag))

    def handle_common_intent(self, message):
        start = "maria"
        target = "joana"
        # what do they have in common
        commons = self.common_this_and_that(start, target)
        for common in commons:
            self.speak(start + " are " + common + " like " + target)

    def handle_relation_intent(self, message):
        start = "maria"
        target = "mammal"
        flag = self.is_this_that(start, target)
        self.speak("answer to is " + start + " a " + target + " is " + str(flag))
        if flag:
            # what is relationship
            nodes = self.crawler.find_shortest_path(start, target)
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
            if commons == []:
                self.speak("I think they don't have anything in common")




    # LILACS helper
    
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
