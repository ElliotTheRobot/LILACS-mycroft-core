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
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger


__author__ = 'jarbas'

logger = getLogger(__name__)


class FeedbackSkill(MycroftSkill):

    def __init__(self):
        super(FeedbackSkill, self).__init__(name="FeedbackSkill")
        self.reload_skill = False

    def initialize(self):

        positive_feedback_intent = IntentBuilder("PositiveFeedbackIntent")\
            .require("PositiveFeedbackKeyword").build()
        self.register_intent(positive_feedback_intent,
                             self.handle_positive_feedback_intent)

        negative_feedback_intent = IntentBuilder("NegativeFeedbackIntent") \
            .require("NegativeFeedbackKeyword").build()
        self.register_intent(negative_feedback_intent,
                             self.handle_negative_feedback_intent)

    def handle_positive_feedback_intent(self, message):
        self.emitter.emit(Message("LILACS_feedback", {"feedback": "positive"}))

    def handle_negative_feedback_intent(self, message):
        self.emitter.emit(Message("LILACS_feedback", {"feedback": "negative"}))

    def stop(self):
        pass


def create_skill():
    return FeedbackSkill()
