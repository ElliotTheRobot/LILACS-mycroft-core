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
# import helper questions functions
from .questions import *

logger = getLogger("Skills")

__authors__ = ["jarbas", "heinzschmidt"]


class LilacsSkill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/28
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/blob/dev/lilacs-core.png
    def __init__(self):
        super(LilacsSkill, self).__init__(name="LilacsSkill")
        self.reload_skill = False

    def initialize(self):
        # build intents
        intro_intent = IntentBuilder("IntroduceLILACSIntent") \
            .require("IntroduceKeyword").build()

        # register intents
        self.register_intent(intro_intent, self.handle_introduce_intent)

    def handle_introduce_intent(self, message):
        self.speak_dialog("whatisLILACS")

    def stop(self):
        pass


def create_skill():
    return LilacsSkill()

