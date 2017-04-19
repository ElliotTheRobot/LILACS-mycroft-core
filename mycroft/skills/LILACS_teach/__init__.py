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


from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACSTeachSkill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/27
    def __init__(self):
        super(LILACSTeachSkill, self).__init__(name="TeachSkill")
        # initialize your variables
        self.reload_skill = False

    def initialize(self):
        # register intents
        self.build_intents()

    def build_intents(self):
        pass

    def stop(self):
        pass


def create_skill():
    return LILACSTeachSkill()