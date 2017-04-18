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
from mycroft.skills.LILACS_core.knowledgeservice import KnowledgeService
from mycroft.skills.LILACS_core.question_parser import LILACSQuestionParser

from mycroft.messagebus.message import Message
from mycroft.skills.LILACS_core.concept import ConceptCrawler, ConceptConnector
# import helper questions functions
from mycroft.skills.LILACS_core.questions import *
from mycroft.skills.LILACS_core.storage import ConceptStorage
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

logger = getLogger("Skills")

__authors__ = ["jarbas", "heinzschmidt"]


class LilacsSkill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/28
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/blob/dev/lilacs-core.png
    def __init__(self):
        super(LilacsSkill, self).__init__(name="LilacsSkill")
        self.reload_skill = False
        self.connector = None
        self.crawler = None
        self.parser = None
        self.service = None
        self.debug = True
        self.answered = False
        self.last_question = ""
        self.last_question_type = ""
        self.last_center = ""
        self.last_target = ""

    def initialize(self):
        self.connector = ConceptConnector(self.emitter)
        self.crawler = ConceptCrawler(self.connector)
        self.parser = LILACSQuestionParser()
        self.service = KnowledgeService(self.emitter)
        self.build_intents()

        self.emitter.on("intent_failure", self.handle_fallback)
        self.emitter.on("multi_utterance_intent_failure", self.handle_multiple_fallback)

        # make thread to keep active
        self.make_bump_thread()

    def ping(self):
        while True:
            i = 0
            self.emitter.emit(Message("recognizer_loop:utterance", {"source": "LILACS_core_skill",
                                                                        "utterances": [
                                                                            "bump LILACS to active skill list"]}))
            while i < 60 * 4:
                i += 1
                sleep(1)
            i = 0

    def make_bump_thread(self):
        timer_thread = Thread(target=self.ping)
        timer_thread.setDaemon(True)
        timer_thread.start()

    def build_intents(self):
        # build intents
        intro_intent = IntentBuilder("IntroduceLILACSIntent") \
            .require("IntroduceKeyword").build()
        bump_intent = IntentBuilder("BumpLILACSSkillIntent"). \
            require("bumpKeyword").build()

        # register intents
        self.register_intent(intro_intent, self.handle_introduce_intent)
        self.register_intent(bump_intent, self.handle_set_on_top_active_list())

    def handle_set_on_top_active_list(self):
        # dummy intent just to bump lilacs core skill to top of active skill list
        # called on a timer in order to always use converse method
        pass

    def handle_introduce_intent(self, message):
        self.speak_dialog("whatisLILACS")

    def parse_utterance(self, utterance):
        # get question type from utterance
        center_node, target_node, parents, synonims, midle, question = self.parser.process_entitys(utterance)
        # TODO try to load concepts from storage
        # TODO input relevant nodes in connector
        # TODO update crawler with new nodes
        # TODO save nodes in storage
        return center_node, target_node, parents, synonims, midle, question

    def deduce_answer(self, utterance):
        # try to undestand what user asks
        center_node, target_node, parents, synonims, midle, question = self.parse_utterance(utterance)
        # update data for feedback
        self.last_center = center_node
        self.last_target = target_node
        self.last_question = utterance
        self.last_question_type = question
        # TODO maybe add question verb to parser, may be needed for disambiguation between types
        # TODO add more question types
        # who|what|when|where|why|which|whose|how|give examples

        # try to answer what user asks depending on question type
        self.answered = False
        if question == "what":
            pass
        elif question == "how":
            self.answered = self.handle_how_intent(utterance)
        elif question == "who":
            pass
        elif question == "when":
            pass
        elif question == "where":
            pass
        elif question == "why":
            self.answered = self.handle_why(center_node, target_node)
        elif question == "which":
            pass
        elif question == "whose":
            pass
        elif question == "talk" or question == "rant":
            pass
        elif question == "in common":
            self.answered = self.handle_relation(center_node, target_node)
        elif question == "is" or question == "are" :
            self.answered = self.handle_compare_intent(center_node, target_node)
        elif question == "give examples":
            self.answered = self.handle_examples_intent(center_node)
        elif question == "unknown":
            self.answered = self.handle_unknown_intent(utterance)

        # if no answer ask user
        if not self.answered:
            self.handle_learning(utterance)

        if self.debug:
            self.speak("utterance : " + utterance)
            self.speak("question type: " + question)
            self.speak("center_node: " + center_node)
            self.speak("target_node: " + target_node)
            self.speak("parents: " + str(parents))
            self.speak("synonims: " + str(synonims))
            self.speak("related: " + str(midle))
            self.speak("answered: " + str(self.answered))

    def handle_talk_about(self, node):
        pass

    def handle_relation(self, center_node, target_node):
        commons = common_this_and_that(center_node, target_node, self.crawler)
        for common in commons:
            self.speak(center_node + " are " + common + " like " + target_node)
        if commons == []:
            self.speak(center_node + " and " + target_node + " have nothing in common")
        return True

    def handle_why(self, center_node, target_node):
        # is this that
        flag = is_this_that(center_node, target_node, self.crawler)
        self.speak("answer to is " + center_node + " a " + target_node + " is " + str(flag))
        if flag:
            # why
            nodes = why_is_this_that(center_node, target_node, self.crawler)
            i = 0
            for node in nodes:
                if node != target_node:
                    self.speak(node + " is " + nodes[i + 1])
                i += 1
        return True

    def handle_how_intent(self, utterance):
        how_to = self.service.adquire(utterance, "wikihow")
        how_to = how_to["wikihow"]
        # TODO check for empty how to and return false
        # the following how_tos are available
        self.speak("the following how tos are available")
        for how in how_to:
            self.speak(how)
        # TODO create intent tree
        # TODO start selection query
        # TODO speak how to
        return True

    def handle_compare_intent(self, center_node, target_node):
        flag = is_this_that(center_node, target_node, self.crawler)
        self.speak("answer to is " + center_node + " a " + target_node + " is " + str(flag))
        return True

    def handle_unknown_intent(self, utterance):
        # get answer from wolfram alpha
        result = self.service.adquire(utterance, "wolfram alpha")
        result = result["wolfram alpha"]
        answer = result["answer"]
        parents = result["parents"]
        synonims = result["synonims"]
        relevant = result["relevant"]
        # TODO load/update nodes
        # say answer to user
        if answer != "no answer":
            self.speak(answer)
            return True
        return False

    def handle_examples_intent(self, node):
        examples = examples_of_this(node, self.crawler)
        for example in examples:
            if example != node:
                self.speak(example + " is an example of " + node)
        if not examples:
            self.speak("i dont know any examples of " + node)
            return False
        else:
            return True

    def handle_what_intent(self, node):
        # TODO read node summary
        # TODO use intent tree to give interactive dialog suggesting examples
        # self.speak("Do you want examples of " + node)
        # activate yes intent
        # use converse method to disable or do something
        return False

    def handle_who_intent(self, node):
        return False

    def handle_when_intent(self, node):
        return False

    def handle_where_intent(self, node):
        return False

    def handle_which_intent(self, node):
        return False

    def handle_whose_intent(self, node):
        return False

    def handle_learning(self, utterance):
        if self.debug:
            self.speak("Searching wolfram alpha")
        self.handle_unknown_intent(utterance)
        # TODO ask user questions about unknown nodes, teach skill handles response

    def handle_fallback(self, message):
        # on single utterance intent failure ask user for correct answer
        utterance = message.data["utterance"]
        self.deduce_answer(utterance)

    def handle_multiple_fallback(self, message):
        # on multiple utterance intent failure ask user for correct answer
        utterances = message.data["utterances"]
        for utterance in utterances:
            self.deduce_answer(utterance)

    def handle_incorrect_answer(self):
        # create nodes / connections for right answer
        #self.last_question = ""
        #self.last_question_type = ""
        #self.last_center = ""
        #self.last_target = ""
        self.speak_dialog("wrong_answer")

    def feedback(self, feedback, utterance):
        # check if previously answered a question
        if feedback == "negative" and self.answered:
            # wrong answer was given, react to negative feedback
            self.handle_incorrect_answer()
        if feedback == "negative" and not self.answered:
            # no apparent reason for negative feedback
            self.speak_dialog("wrong_answer_confused")

    def stop(self):
        pass

def create_skill():
    return LilacsSkill()

