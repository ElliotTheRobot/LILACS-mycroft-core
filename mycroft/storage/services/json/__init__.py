from mycroft.storage.services import StorageBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

__author__ = '..'

logger = getLogger(abspath(__file__).split('/')[-2])


class JsonService(StorageBackend):
    def __init__(self, config, emitter, name='json'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('JsonStorageLoad', self._load)
        self.emitter.on('JsonStorageLoad', self._save)

    def _load(self, message=None):
        logger.info('JsonStorage_Load')
        node = message.data["node"]
        if node is None:
            logger.error("No node to load")
            return
        else:
            #TODO load node here
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
