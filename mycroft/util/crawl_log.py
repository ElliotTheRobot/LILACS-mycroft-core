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


import logging


__author__ = 'seanfitz'

#TODO read from config
# for some reason log files are always empty, look at this later

path = "/home/user/mycroft-core/mycroft/skills/LILACS/crawl_logs"

def getLogger(name="Crawler", crawl_type="Drunk"):
    """
    Get a python crawler logger

    :param name: Module name for the logger

    :param crawl_type: Type of crawling
    
    :return: an instance of logging.Logger
    """

    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    crawler_log_path = path + "/" + crawl_type + "_" + name + ".log"
    logging.basicConfig(filename=crawler_log_path, format=FORMAT, level=logging.DEBUG)
    return logging.getLogger(crawl_type+" "+name)
