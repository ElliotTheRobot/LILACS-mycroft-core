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


import json
from os.path import expanduser, exists, abspath, dirname, basename, isdir, join
from os import listdir
import sys
import time
import imp

from mycroft.configuration import ConfigurationManager
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.util.log import getLogger

__author__ = 'jarbas'

MainModule = '__init__'
sys.path.append(abspath(dirname(__file__)))
logger = getLogger("KnowledgeBackend")

ws = None

default = None
service = []
current = None


def create_service_descriptor(service_folder):
    """Prepares a descriptor that can be used together with imp."""
    info = imp.find_module(MainModule, [service_folder])
    return {"name": basename(service_folder), "info": info}


def get_services(services_folder):
    """Load and initialize services from all subfolders."""
    logger.info("Loading services from " + services_folder)
    services = []
    possible_services = listdir(services_folder)
    for i in possible_services:
        location = join(services_folder, i)
        if (isdir(location) and
                not MainModule + ".py" in listdir(location)):
            for j in listdir(location):
                name = join(location, j)
                if (not isdir(name) or
                        not MainModule + ".py" in listdir(name)):
                    continue
                try:
                    services.append(create_service_descriptor(name))
                except:
                    logger.error('Failed to create service from ' + name,
                                 exc_info=True)
        if (not isdir(location) or
                not MainModule + ".py" in listdir(location)):
            continue
        try:
            services.append(create_service_descriptor(location))
        except:
            logger.error('Failed to create service from ' + name,
                         exc_info=True)
    return sorted(services, key=lambda p: p.get('name'))


def load_services(config, ws):
    """Search though the service directory and load any services."""
    logger.info("Loading services")
    service_directories = get_services(dirname(abspath(__file__)) +
                                       '/services/')
    service = []
    for descriptor in service_directories:
        logger.info('Loading ' + descriptor['name'])
        service_module = imp.load_module(descriptor["name"] + MainModule,
                                         *descriptor["info"])
        if (hasattr(service_module, 'autodetect') and
                callable(service_module.autodetect)):
            s = service_module.autodetect(config, ws)
            service += s
        if (hasattr(service_module, 'load_service')):
            s = service_module.load_service(config, ws)
            service += s

    return service


def load_services_callback():
    global ws
    global default
    global service

    config = ConfigurationManager.get().get("Knowledge")
    service = load_services(config, ws)
    logger.info(service)
    default_name = config.get('default-backend', '')
    logger.info('Finding default backend...')
    for s in service:
        logger.info('checking ' + s.name)
        if s.name == default_name:
            default = s
            logger.info('Found ' + default.name)
            break
    else:
        default = None
        logger.info('no default found')
    logger.info('Default:' + str(default))

    # do stuff
    ws.on('LILACS_KnowledgeService_adquire', _adquire)
    ws.on('mycroft.stop', _stop)


def _stop(message=None):
    """
        Handler for MycroftStop. Stops any knowledge service.
    """
    global current
    logger.info('stopping all knowledge services')
    print current
    if current:
        current.stop()
        current = None
    logger.info('Stopped')


def adquire(subject, prefered_service):
    """
        play seeking knwoledge on the prefered service if it supports
        the uri. If not the next best backend is found.
    """
    global current
    logger.info('adquire')
    _stop()
    # check if user requested a particular service
    if prefered_service:
        service = prefered_service
    # check if default supports the uri
    elif default:
        logger.info("Using default backend")
        logger.info(default.name)
        service = default
    else:  # Fall back to asking user?
        logger.error("no service")
        return
    service.set_subject(subject)
    service.adquire()
    current = service


def _adquire(message):
    """
        Handler for LILACS_KnowledgeService_adquire. Starts seeking knowledge about.... Also
        determines if the user requested a special service.
    """
    global service
    logger.info('LILACS_KnowledgeService_adquire')
    logger.info(message.data['subject'])

    subject = message.data['subject']

    # Find if the user wants to use a specific backend
    for s in service:
        logger.info(s.name)
        if s.name in message.data['utterance']:
            prefered_service = s
            logger.info(s.name + ' would be prefered')
            break
    else:
        prefered_service = None

    adquire(subject, prefered_service)


def connect():
    global ws
    ws.run_forever()


def main():
    global ws
    ws = WebsocketClient()
    ConfigurationManager.init(ws)

    def echo(message):
        try:
            _message = json.loads(message)

            if _message.get("type") == "registration":
                # do not log tokens from registration messages
                _message["data"]["token"] = None
            message = json.dumps(_message)
        except:
            pass
        logger.debug(message)

    logger.info("Staring Knowledge Services")
    ws.on('message', echo)
    ws.once('open', load_services_callback)
    ws.run_forever()


if __name__ == "__main__":
    main()
