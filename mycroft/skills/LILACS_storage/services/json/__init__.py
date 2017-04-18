import json
from os import listdir
from os.path import abspath, dirname

from mycroft.messagebus.message import Message
from mycroft.skills.LILACS_storage.services import StorageBackend
from mycroft.util.log import getLogger

__author__ = ['jarbasai', 'elliottherobot']

logger = getLogger(abspath(__file__).split('/')[-2])


class JsonService(StorageBackend):

    def __init__(self, config, emitter, name='json'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('JsonStorageLoad', self._load)
        self.emitter.on('JsonStorageLoad', self._save)
        self._dataJSON = {}
        self._dataConnStatus = 0

    def _load(self, message=None):
        logger.info('JsonStorage_Load')
        node = message.data["node"]
        if node is None:
            logger.error("No node to load")
            return
        else:
            # check to see if there is a json file for this node (supernode), else load default
            storagepath = str(dirname(__file__) + "/jsondata/")
            loaded = False
            for file in listdir(storagepath):
                if file(str(node) + ".json"):
                    self.datastore_connect(self.name, storagepath + str(node) + ".json")
                    loaded = True
            if not loaded:
                self.datastore_connect(self.name, storagepath + "default.json")
                loaded = True

            if loaded:
                # check if the json file was read successfully
                if self._dataConnStatus == 1:
                    return self._dataJSON
            else:
                # no json files read, return empty dict
                return {}

            pass

    def _save(self, message=None):
        logger.info('JsonStorage_Save')
        node = message.data["node"]
        if node is None:
            logger.error("No node to save")
            return
        else:
            #TODO save node here
            pass

    def load(self, node):
        logger.info('Call JsonStorageLoad')
        self.emitter.emit(Message('JsonStorageLoad', {"node": node}))

    def save(self, node):
        logger.info('Call JsonStorageSave')
        self.emitter.emit(Message('JsonStorageSave', {"node": node}))

    def datastore_connect(self, data_format="json", data_source=""):
        if(data_format == "json"):
            with open(data_source, 'r') as myfile:
                file_content = myfile.read().replace("{}", "")
                self._dataJSON = json.loads(file_content)
            if (self._dataJSON):
                self._dataConnStatus = 1
            else:
                self._dataConnStatus = 0
        # if(data_format == "xml"):
        # if(data_format == "sql"):
        # if(data_format == "xmlhttp"):

    def stop(self):
        logger.info('JsonStorage_Stop')
        if self.process:
            self.process.terminate()
            self.process = None


def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'json']
    instances = [JsonService(s[1], emitter, s[0]) for s in services]
    return instances
