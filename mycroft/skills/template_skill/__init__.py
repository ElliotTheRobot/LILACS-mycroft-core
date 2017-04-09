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


class TemplateSkill(MycroftSkill):

    def __init__(self):
        super(TemplateSkill, self).__init__(name="TemplateSkill")
        # initialize your variables
        self.flag = False
        # concept connector
        self.knowledge = ConceptConnector()

    def initialize(self):
        # initialize self intent parser
        self.intent_parser = IntentParser(self.emitter)
        # register intents
        self.build_intents()
        # make tree
        self.build_intent_tree()
        # create concepts
        self.create_concepts()

    def build_intents(self):
        # build
        enable_second_intent = IntentBuilder("FirstIntent") \
            .require("FirstKeyword").build()
        second_intent = IntentBuilder("SecondIntent") \
            .require("SecondKeyword").build()

        # register intents
        self.register_intent(enable_second_intent,
                             self.handle_enable_second_intent)
        self.register_intent(second_intent,
                             self.handle_second_intent)

    def build_intent_tree(self):
        layers = [["FirstIntent"], ["SecondIntent"]]
        timer_timeout_in_seconds = 60
        self.tree = IntentTree(self.emitter, layers, timer_timeout_in_seconds)
        # not sure where to put this in core, should be in initialize of every skill
        self.emitter.on('enable_intent', self.handle_enable_intent)
        self.emitter.on('disable_intent', self.handle_disable_intent)

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
    
    def handle_enable_second_intent(self, message):
        # do stuff
        # climb intent tree
        self.tree.next()

    def handle_second_intent(self, message):
        # do stuff
        # go back to level one or next or previous...
        self.tree.reset()
    
    # LILACS helper
    
    def is_this_that(self, this, that, crawler=None):
        if crawler is None:
            crawler = ConceptCrawler(concept_connector=self.knowledge)
        flag = crawler.drunk_crawl(this, that)
        return flag

    def examples_of_this(self, this, crawler=None):
        if crawler is None:
            crawler = ConceptCrawler(concept_connector=self.knowledge)
        crawler.drunk_crawl(this, "no target crawl", direction="childs")
        examples = []
        for example in crawler.crawled:
            examples.append(example)
        return examples

    def common_this_and_that(self, this, that, crawler=None):
        if crawler is None:
            crawler = ConceptCrawler(concept_connector=self.knowledge)
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
        # reset intents to start-up state if desired
        self.tree.reset()

    def converse(self, transcript, lang="en-us"):
        # determine self intent from transcript
        determined, intent = self.intent_parser.determine_intent(transcript)
        if not determined:
            # check for any conditions
            # wrong sequence entry
            self.tree.reset()
            # in here handle the utterance if it doesnt trigger a self intent
            if self.flag:
                # keep listening without wakeword
                self.speak("handle utterance manually here", expect_response=True)
                return True

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
    return TemplateSkill()