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


from threading import Thread
from time import sleep

from adapt.intent import IntentBuilder

from mycroft.messagebus.message import Message
from mycroft.skills.LILACS_core.question_parser import LILACSQuestionParser
from mycroft.skills.LILACS_knowledge.knowledgeservice import KnowledgeService
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACSCuriositySkill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/19
    def __init__(self):
        super(LILACSCuriositySkill, self).__init__(name="CuriositySkill")
        # initialize your variables
        self.reload_skill = False
        self.active = True
        self.get_node_info = False
        self.parser = None
        self.service = None
        self.TIMEOUT = 2

    def initialize(self):
        # register intents
        self.parser = LILACSQuestionParser()
        self.service = KnowledgeService(self.emitter)
        self.build_intents()

        # make thread to keep active
        self.make_bump_thread()

    def ping(self):
        while True:
            i = 0
            if self.active:
                self.emitter.emit(Message("recognizer_loop:utterance", {"source": "LILACS_curiosity_skill",
                                                                    "utterances": [
                                                                        "bump curiosity to active skill list"]}))
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
        if "bump curiosity" not in transcript[0]:
            nodes, parents, synonims = self.parser.tag_from_dbpedia(transcript[0])
            self.log.info("nodes: " + str(nodes))
            self.log.info("parents: " + str(parents))
            self.log.info("synonims: " + str(synonims))
            # if flag get info for nodes
            # TODO use appropriate backends
            if self.get_node_info:
                backend = "dbpedia"
                for node in nodes:
                    node_info = self.service.adquire(node, backend)
                    print node_info

            #signal core to create nodes
            for node in nodes:
                node_dict = {}
                node_dict.setdefault("node_name", node)
                node_dict.setdefault("parents", {})
                node_dict.setdefault("childs", {})
                node_dict.setdefault("synonims", [])
                node_dict.setdefault("antonims", [])
                node_dict.setdefault("data", {})
                self.emitter.emit(Message("new_node", node_dict))
            for node in parents:
                node_dict = {}
                node_dict.setdefault("node_name", node)
                node_dict.setdefault("parents", parents[node])
                node_dict.setdefault("childs", {})
                node_dict.setdefault("synonims", [])
                node_dict.setdefault("antonims", [])
                node_dict.setdefault("data", {})
                self.emitter.emit(Message("new_node", node_dict))
            for node in synonims:
                node_dict = {}
                node_dict.setdefault("node_name", node)
                node_dict.setdefault("parents", {})
                node_dict.setdefault("childs", {})
                node_dict.setdefault("synonims", [synonims[node]])
                node_dict.setdefault("antonims", [])
                node_dict.setdefault("data", {})
                self.emitter.emit(Message("new_node", node_dict))

        # tell intent skill you did not handle intent
        return False

def create_skill():
    return LILACSCuriositySkill()