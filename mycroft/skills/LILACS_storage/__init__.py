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
from mycroft.skills.LILACS_storage.main import main as service

from threading import Thread

__author__ = 'jarbas'

logger = getLogger(__name__)


class LILACS_Storage_Skill(MycroftSkill):
    def __init__(self):
        super(LILACS_Storage_Skill, self).__init__(name="LILACS_Storage_Skill")

    def initialize(self):
        timer_thread = Thread(target=self.service)
        timer_thread.setDaemon(True)
        timer_thread.start()

    def service(self):
        service()


def create_skill():
    return LILACS_Storage_Skill()