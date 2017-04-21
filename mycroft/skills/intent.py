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


from adapt.engine import IntentDeterminationEngine

from mycroft.messagebus.message import Message
from mycroft.skills.intent_parser import IntentParser
from mycroft.util.log import getLogger

import time

__author__ = 'seanfitz'

logger = getLogger(__name__)


class Intent(object):
    def __init__(self, emitter):
        self.engine = IntentDeterminationEngine()
        self.emitter = emitter
        self.intent_parser = IntentParser(self.emitter)
        self.active_skills = []  # [skill_id , timestamp]
        self.converse_timeout = 5  # minutes to prune active_skills
        self.emitter.on('register_intent', self.handle_register_intent)
        self.emitter.on('recognizer_loop:utterance', self.handle_utterance)
        self.emitter.on('converse_status_response', self.handle_conversation_response)

    def do_conversation(self, utterances, skill_id, lang):
        self.emitter.emit(Message("converse_status_request", {
            "skill_id": skill_id, "utterances": utterances, "lang": lang}))
        self.waiting = True
        self.result = False
        while self.waiting:
            pass
        return self.result

    def handle_conversation_response(self, message):
        # id = message.data["skill_id"]
        # no need to crosscheck id because waiting before new request is made
        # no other skill will make this request is safe assumption
        result = message.data["result"]
        self.result = result
        self.waiting = False

    def remove_active_skill(self, skill_id):
        for skill in self.active_skills:
            if skill[0] == skill_id:
                self.active_skills.remove(skill)

    def add_active_skill(self, skill_id):
        # you have to search the list for an existing entry that already contains it and remove that reference
        self.remove_active_skill(skill_id)
        # add skill with timestamp to start of skill_list
        self.active_skills.insert(0, [skill_id, time.time()])

    def handle_utterance(self, message):
        # Get language of the utterance
        lang = message.data.get('lang', None)
        if not lang:
            lang = "en-us"

        utterances = message.data.get('utterances', '')
        # check for conversation time-out
        self.active_skills = [skill for skill in self.active_skills
                              if time.time() - skill[1] <= self.converse_timeout * 60]

        # check if any skill wants to handle utterance
        for skill in self.active_skills:
            if self.do_conversation(utterances, skill[0], lang):
                # update timestamp, or there will be a timeout where
                # intent stops conversing whether its being used or not
                self.add_active_skill(skill[0])
                return
        # no skill wants to handle utterance, proceed

        best_intent = None
        success = False

        try:
            success, best_intent = self.intent_parser.determine_intent(utterances, lang)
        except:
            logger.error("Could not determine best intent")

        if success:
            self.intent_parser.execute_intent()

            skill_id = int(best_intent['intent_type'].split(":")[0])

            self.add_active_skill(skill_id)

        elif len(utterances) == 1:
            self.emitter.emit(Message("intent_failure", {
                "utterance": utterances[0],
                "lang": lang
            }))
        else:
            self.emitter.emit(Message("multi_utterance_intent_failure", {
                "utterances": utterances,
                "lang": lang
            }))

    def handle_register_intent(self, message):
        intent = message.data
        self.intent_parser.register_intent(intent)
