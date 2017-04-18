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

from mycroft.skills.LILACS_core.concept import ConceptConnector, ConceptCrawler
from mycroft.skills.LILACS_core.questions import *

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACS_curiosity_skill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/19
    def __init__(self):
        super(LILACS_curiosity_skill, self).__init__(name="CuriositySkill")
        # initialize your variables
        self.reload_skill = False
        self.active = False

    def initialize(self):
        # register intents
        self.build_intents()
        self.handle_activate_intent("start_up activation")

    def build_intents(self):
        # build intents
        deactivate_intent = IntentBuilder("DeactivateCuriosityIntent") \
            .require("deactivateKeyword").build()
        activate_intent=IntentBuilder("ActivateCuriosityIntent") \
            .require("activateKeyword").build()

        # register intents
        self.register_intent(deactivate_intent, self.handle_deactivate_intent)
        self.register_intent(activate_intent, self.handle_activate_intent)

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
        # signal core to create nodes
        # if flag get info for nodes

        # tell intent skill you did not handle intent
        return False

def create_skill():
    return LILACS_curiosity_skill()