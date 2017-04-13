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

from mycroft.skills.LILACS.concept import ConceptConnector, ConceptCrawler
from mycroft.skills.LILACS.storage import ConceptStorage

from os.path import dirname

storagepath = ""

logger = getLogger("Skills")

__authors__ = ["jarbas", "heinzschmidt"]

class LilacsSkill(MycroftSkill):

    def __init__(self):
        super(LilacsSkill, self).__init__(name="LilacsSkill")
        self.reload_skill = False

    def initialize(self):
        intro_intent = IntentBuilder("IntroduceLILACSIntent") \
            .require("IntroduceKeyword").build()

        # register intents
        self.register_intent(intro_intent, self.handle_introduce_intent)

        self.storagepath = str(dirname(__file__) + "/.db/")

        self.register_regex("(?P<SubjectWord1>.*)")
        self.register_regex("(?P<ObjectWord1>.*)")

        # example usage: Is Joana a human?
        #

        is_intent = IntentBuilder("IsIntent") \
            .require("SubjectWord1") \
            .require("ObjectWord1") \
            .build()

        self.register_intent(is_intent, self.handle_is_intent)

    def handle_introduce_intent(self, message):
        self.speak_dialog("whatisLILACS")


    def handle_is_intent(self, message):

        self.speak(message.data.get("SubjectWord1"))
        self.speak(message.data.get("ObjectWord1"))

        storage_inst = ConceptStorage(self.storagepath)

        self.speak("Storage class created")

        nodes = storage_inst.get_nodes_names()

        for node in nodes:
            self.speak(node)
        try:

            knowledge = ConceptConnector(concepts=nodes)

            if(knowledge.is_storage_loaded()):
                self.speak("Storage loaded")
            else:
                self.speak("Not loaded")

        except Exception as Mainerr:
            self.speak("Mainerr " + str(Mainerr.message))

    # standard questions helper functions
    def is_this_that(self, this, that, crawler):
        flag = crawler.drunk_crawl(this, that)
        return flag

    def examples_of_this(self, this, crawler):
        crawler.drunk_crawl(this, "no target crawl", direction="childs")
        examples = []
        for example in crawler.crawled:
            examples.append(example)
        return examples

    def common_this_and_that(self, this, that, crawler):
        crawler.drunk_crawl(this, "no target crawl")
        p_crawl = crawler.crawled
        common = []
        for node in p_crawl:
            flag = crawler.drunk_crawl(that, node)
            if flag:
                common.append(node)
        return common

    def stop(self):
        pass


def create_skill():
    return LilacsSkill()

