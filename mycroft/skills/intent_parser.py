from adapt.engine import IntentDeterminationEngine
from adapt.intent import Intent
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

import time
from multiprocessing import Process

from mycroft.util.parse import normalize

__author__ = 'jarbas'

logger = getLogger(__name__)


class IntentTree():
    def __init__(self, emitter, layers = [], timer = 500):
        self.emitter = emitter
        # make intent tree for N layers
        self.tree = []
        self.current_layer = 0
        self.timer = timer
        self.timer_thread = None
        for layer in layers:
            self.add_layer(layer)
        self.activate_layer(0)

    def disable_intent(self, intent_name):
        """Disable a registered intent"""
        self.emitter.emit(Message("disable_intent", {"intent_name": intent_name}))

    def enable_intent(self, intent_name):
        """Reenable a registered self intent"""
        self.emitter.emit(Message("enable_intent", {"intent_name": intent_name}))

    def start_timer(self):

        self.stop_timer()

        # set new timer
        def timer():
            logger.info("New Timer Started")
            start_time = time.time()
            while time.time() - start_time <= self.timer:
                time.sleep(1)
            # on end of timer reset tree
            logger.info("Timer Ended - resetting tree")
            self.reset()

        self.timer_thread = Process(target=timer)
        self.timer_thread.start()

    def stop_timer(self):
        logger.info("Stopping previous timer")
        try:
            # cancel previous timers
            self.timer_thread.terminate()
        except:
            pass

    def reset(self):
        logger.info("Reseting Tree")
        self.stop_timer()
        self.activate_layer(0)

    def next(self):
        logger.info("Going to next Tree Layer")
        self.current_layer += 1
        if self.current_layer > len(self.tree):
            logger.info("Already in last layer, going to layer 0")
            self.current_layer = 0
        if self.current_layer != 0:
            self.start_timer()
        self.activate_layer(self.current_layer)

    def previous(self):
        logger.info("Going to previous Tree Layer")
        self.current_layer -= 1
        if self.current_layer < 0:
            self.current_layer = len(self.tree)
            logger.info("Already in layer 0, going to last layer")
        if self.current_layer != 0:
            self.start_timer()
        self.activate_layer(self.current_layer)

    def add_layer(self, intent_list=[]):
        self.tree.append(intent_list)
        logger.info("Adding layer to tree " + str(intent_list))

    def replace_layer(self, layer_num, intent_list=[]):
        logger.info("Removing layer number " + str(layer_num) + " from tree ")
        self.tree.pop(layer_num)
        self.tree[layer_num] = intent_list
        logger.info("Adding layer" + str(intent_list) + " to tree in position " + str(layer_num) )

    def remove_layer(self, layer_num):
        self.tree.pop(layer_num)
        logger.info("Removing layer number " + str(layer_num) + " from tree ")

    def find_layer(self, intent_list=[]):
        layer_list = []
        for i in range(0, len(self.tree)):
            if self.tree[i] == intent_list:
                layer_list.append(i)
        return layer_list

    def disable(self):
        logger.info("Disabling tree")
        # disable all tree layers
        for i in range(0, len(self.tree)):
            self.deactivate_layer(i)

    def activate_layer(self, layer_num):
        # error check
        if layer_num < 0 or layer_num > len(self.tree):
            logger.error("invalid layer number")
            return

        self.current_layer = layer_num

        # disable other layers
        self.disable()

        # TODO in here we should wait for all intents to be detached
        # sometimes detach intent from this step comes after register from next
        time.sleep(0.3)

        # enable layer
        logger.info("Activating Layer " + str(layer_num))
        for intent_name in self.tree[layer_num]:
            self.enable_intent(intent_name)

    def deactivate_layer(self, layer_num):
        # error check
        if layer_num < 0 or layer_num > len(self.tree):
            logger.error("invalid layer number")
            return
        logger.info("Deactivating Layer " + str(layer_num))
        for intent_name in self.tree[layer_num]:
            self.disable_intent(intent_name)


class IntentParser():
    def __init__(self, emitter):
        self.engine = IntentDeterminationEngine()
        self.emitter = emitter
        self.reply = None
        self.emitter.on('register_vocab', self.handle_register_vocab)
        self.emitter.on('detach_intent', self.handle_detach_intent)

    def register_intent(self, intent_dict, handler=None):

        intent = Intent(intent_dict.get('name'),
                      intent_dict.get('requires'),
                      intent_dict.get('at_least_one'),
                      intent_dict.get('optional'))
        self.engine.register_intent_parser(intent)

        def receive_handler(message):
            try:
                handler(message)
            except:
                # TODO: Localize
                logger.error(
                    "An error occurred while processing a request in IntentParser", exc_info=True)

        if handler is not None:
            self.emitter.on(intent_dict.get('name'), receive_handler)

    def determine_intent(self, utterances, lang="en-us"):
        best_intent = None
        self.reply = None
        for utterance in utterances:
            try:
                # normalize() changes "it's a boy" to "it is boy", etc.
                best_intent = next(self.engine.determine_intent(
                    normalize(utterance, lang), 100))

                # TODO - Should Adapt handle this?
                best_intent['utterance'] = utterance
            except StopIteration, e:
                logger.exception(e)
                continue
        if best_intent and best_intent.get('confidence', 0.0) > 0.0:
            self.reply = Message(best_intent.get('intent_type'), best_intent)
            return True, best_intent

        return False, best_intent

    def execute_intent(self, intent=None):
        if intent and intent.get('confidence', 0.0) > 0.0:
            self.reply = Message(intent.get('intent_type'), intent)

        if self.reply is not None:
            self.emitter.emit(self.reply)
            # self.reply = None #actually its nice to be able to call execute_intent as many times as wanted
            return True
        return False

    def handle_register_vocab(self, message):
        start_concept = message.data.get('start')
        end_concept = message.data.get('end')
        regex_str = message.data.get('regex')
        alias_of = message.data.get('alias_of')
        if regex_str:
            self.engine.register_regex_entity(regex_str)
        else:
            self.engine.register_entity(
                start_concept, end_concept, alias_of=alias_of)

    def handle_detach_intent(self, message):
        intent_name = message.data.get('intent_name')
        new_parsers = [
            p for p in self.engine.intent_parsers if p.name != intent_name]
        self.engine.intent_parsers = new_parsers
