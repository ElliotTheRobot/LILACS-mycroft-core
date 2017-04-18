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
from mycroft.messagebus.message import Message

from mycroft.skills.question_parser import LILACSQuestionParser
from mycroft.skills.knowledgeservice import KnowledgeService

from time import sleep
from threading import Thread

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACS_curiosity_skill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/19
    def __init__(self):
        super(LILACS_curiosity_skill, self).__init__(name="CuriositySkill")
        # initialize your variables
        self.reload_skill = False
        self.active = False
        self.get_node_info = True
        self.parser = None
        self.service = None
        self.TIMEOUT = 2

    def initialize(self):
        # register intents
        self.parser = LILACSQuestionParser()
        self.service = KnowledgeService(self.emitter)
        self.build_intents()
        #self.handle_activate_intent("start_up activation")

        # make thread to keep active
        self.make_bump_thread()

    def ping(self):
        while True:
            i = 0
            if self.active:
                self.emitter.emit(Message("recognizer_loop:utterance", {"source": "LILACS_curiosity_skill",
                                                                    "utterances": [
                                                                        "bump LILACS to active skill list"]}))
            while i < 60 * self.TIMEOUT:
                i += 1
                sleep(1)
            i = 0

    def make_bump_thread(self):
        timer_thread = Thread(target=self.ping)
        timer_thread.setDaemon(True)
        timer_thread.start()

    def build_intents(self):
        # build intents
        deactivate_intent = IntentBuilder("DeactivateCuriosityIntent") \
            .require("deactivateKeyword").build()
        activate_intent=IntentBuilder("ActivateCuriosityIntent") \
            .require("activateKeyword").build()

        bump_intent = IntentBuilder("BumpCuriositySkillIntent"). \
            require("bumpKeyword").build()

        # register intents
        self.register_intent(deactivate_intent, self.handle_deactivate_intent)
        self.register_intent(activate_intent, self.handle_activate_intent)
        self.register_intent(bump_intent, self.handle_set_on_top_active_list())

    def handle_set_on_top_active_list(self):
        # dummy intent just to bump curiosity skill to top of active skill list
        # called on a timer in order to always use converse method
        pass

    def handle_deactivate_intent(self, message):
        self.active = False
        self.speak_dialog("curiosity_off")

    def handle_activate_intent(self, message):
        self.active = True
        self.speak_dialog("curiosity_on")

    def stop(self):
        self.handle_deactivate_intent("global stop")

    def converse(self, transcript, lang="en-us"):
        # parse all utterances for entitys
        if transcript[0] != "bump curiosity to active skill list":
            nodes, parents, synonims = self.parser.tag_from_dbpedia(transcript[0])
            print "nodes: " + str(nodes)
            print "parents: " + str(parents)
            print "synonims: " + str(synonims)

            # if flag get info for nodes
            # TODO use appropriate backends
            if self.get_node_info:
                backend = "dbpedia"
                for node in nodes:
                    node_info = self.service.adquire(node, backend)
                    print node_info

            # TODO signal core to create nodes
            pass

        # tell intent skill you did not handle intent
        return False

def create_skill():
    return LILACS_curiosity_skill()