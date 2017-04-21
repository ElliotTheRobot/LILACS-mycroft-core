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

from threading import Thread
from time import sleep
import random

from adapt.intent import IntentBuilder

from mycroft.messagebus.message import Message
from mycroft.skills.LILACS_core.concept import ConceptConnector
from mycroft.skills.LILACS_core.crawler import ConceptCrawler
from mycroft.skills.LILACS_core.question_parser import LILACSQuestionParser
# import helper questions functions
from mycroft.skills.LILACS_core.questions import *
from mycroft.skills.LILACS_knowledge.knowledgeservice import KnowledgeService
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

logger = getLogger("Skills")

__authors__ = ["jarbas", "heinzschmidt"]


class LilacsCoreSkill(MycroftSkill):
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/28
    # https://github.com/ElliotTheRobot/LILACS-mycroft-core/blob/dev/lilacs-core.png
    def __init__(self):
        super(LilacsCoreSkill, self).__init__(name="LilacsCoreSkill")
        self.reload_skill = False
        self.connector = None
        self.crawler = None
        self.parser = None
        self.service = None
        self.debug = False
        self.answered = False
        self.last_question = ""
        self.last_question_type = ""
        self.last_center = ""
        self.last_target = ""

    def initialize(self):

        self.emitter.on("intent_failure", self.handle_fallback)
        self.emitter.on("multi_utterance_intent_failure", self.handle_multiple_fallback)
        self.emitter.on("LILACS_feedback", self.feedback)

        self.parser = LILACSQuestionParser()
        self.service = KnowledgeService(self.emitter)
        self.build_intents()

        self.connector = ConceptConnector(emitter=self.emitter)
        self.create_concepts()
        self.crawler = ConceptCrawler(self.connector)

    def build_intents(self):
        # build intents
        intro_intent = IntentBuilder("IntroduceLILACSIntent") \
            .require("IntroduceKeyword").build()
        nodes_intent = IntentBuilder("ListNodesIntent"). \
            require("nodesKeyword").build()

        # register intents
        self.register_intent(intro_intent, self.handle_introduce_intent)
        self.register_intent(nodes_intent, self.handle_list_nodes_intent)

    # debug methods
    def create_concepts(self):
        # this is just for debug purposes
        if self.debug:
            self.speak("creating standard nodes for debugging")
            name = "human"
            child_concepts = {}
            parent_concepts = {"animal": 2, "mammal": 1}
            self.connector.create_concept(name, parent_concepts=parent_concepts,
                                          child_concepts=child_concepts)

            name = "animal"
            child_concepts = {"frog": 1}
            parent_concepts = {}
            self.connector.create_concept(name, parent_concepts=parent_concepts,
                                          child_concepts=child_concepts)

    def handle_list_nodes_intent(self, message):
        nodes = self.connector.get_concept_names()
        self.speak("the following nodes are available")
        if nodes == []:
            self.speak("none")
        for node in nodes:
            self.speak(node)

    # standard intents
    def handle_introduce_intent(self, message):
        self.speak_dialog("whatisLILACS")

    # core methods
    def parse_utterance(self, utterance):
        # get question type from utterance
        center_node, target_node, parents, synonims, midle, question = self.parser.process_entitys(utterance)
        # TODO try to load concepts from storage
        # TODO input relevant nodes in connector
        # TODO update crawler with new nodes
        # TODO save nodes in storage
        return center_node, target_node, parents, synonims, midle, question

    def deduce_answer(self, utterance):
        # try to undestand what user asks
        center_node, target_node, parents, synonims, midle, question = self.parse_utterance(utterance)
        if center_node is None or center_node == "":
            self.speak("i dont understand the question")
            self.answered = self.handle_learning(utterance)
            return

        # update data for feedback
        self.last_center = center_node
        self.last_target = target_node
        self.last_question = utterance
        self.last_question_type = question
        # TODO maybe add question verb to parser, may be needed for disambiguation between types
        # TODO add more question types
        if self.debug:
            self.speak("Pre-processing of utterance : " + utterance)
            self.speak("question type: " + question)
            self.speak("center_node: " + center_node)
            self.speak("target_node: " + target_node)
            self.speak("parents: " + str(parents))
            self.speak("synonims: " + str(synonims))
            self.speak("related: " + str(midle))

        # update nodes in connector
        nodes = []
        nodes.append(center_node)
        nodes.append(target_node)
        for node in midle:
            nodes.append(node)
        #nodes += midle
        childs = {}
        antonims = {}
        self.log.info("utterance : " + utterance)
        self.log.info("question type: " + question)
        self.log.info("center_node: " + center_node)
        self.log.info("target_node: " + target_node)
        self.log.info("parents: " + str(parents))
        self.log.info("synonims: " + str(synonims))
        self.log.info("related: " + str(midle))
        self.handle_update_connector(nodes, parents, childs, synonims, antonims)
        # try to answer what user asks depending on question type
        self.answered = False
        if question == "what":
            self.answered = self.handle_what_intent(center_node)
        elif question == "how":
            self.answered = self.handle_how_intent(utterance)
        elif question == "who":
            # TODO find a good backend for persons only!
            self.answered = self.handle_what_intent(center_node)
        elif question == "when":
            pass
        elif question == "where":
            pass
        elif question == "why":
            self.answered = self.handle_why(center_node, target_node)
        elif question == "which":
            pass
        elif question == "whose":
            pass
        elif question == "talk" or question == "rant":
            self.answered = self.handle_talk_about(center_node, target_node, utterance)
        elif question == "in common":
            self.answered = self.handle_relation(center_node, target_node)
        elif question == "is" or question == "are" :
            self.answered = self.handle_compare_intent(center_node, target_node)
        elif question == "examples":
            self.answered = self.handle_examples_intent(center_node)
        else:# question == "unknown":
            self.answered = self.handle_unknown_intent(utterance)

        # if no answer ask user
        if not self.answered:
            self.answered = self.handle_learning(utterance)

        self.log.info("answered: " + str(self.answered))
        if self.debug:
            self.speak("answered: " + str(self.answered))

    def handle_update_connector(self, nodes=[], parents={}, childs={}, synonims={}, antonims={}, data={}):
        # nodes = [ node_names ]
        # parents = { node_name: [node_parents] }
        # childs = { node_name: [node_childs] }
        # synonims = { node_name: [node_synonims] }
        # antonims = { node_name: [node_antonims] }

        # create_concept(self, new_concept_name, data={},
        #                   child_concepts={}, parent_concepts={}, synonims=[], antonims=[])

        # TODO update storage
        # make empty nodes
        for node in nodes:
            self.log.info("processing node: " + node)
            if node is not None and node != "" and node != " ":
                self.connector.create_concept(node, parent_concepts={}, child_concepts= {},synonims= [], antonims=[], data={} )
        # make all nodes with parents
        for node in parents:
            self.log.info("processing parents of node: " + node)
            if node is not None and node != "" and node != " ":
                pdict = {}
                for p in parents[node]:
                    self.log.info("parent: " + p)
                    pdict.setdefault(p, 5)  # gen 5 for auto-adquire
                self.connector.create_concept(node, parent_concepts=pdict, child_concepts= {},synonims= [], antonims=[], data={})
        # make all nodes with childs
        for node in childs:
            self.log.info("processing childs of node: " + node)
            if node is not None and node != "" and node != " ":
                cdict = {}
                for c in childs[node]:
                    self.log.info("child: " + c)
                    cdict.setdefault(c, 5)  # gen 5 for auto-adquire
                self.connector.create_concept(node, child_concepts=cdict, parent_concepts= {}, synonims= [], antonims=[], data={})
        # make all nodes with synonims
        for node in synonims:
            self.log.info("processing synonims of node: " + node)
            if node is not None and node != "" and node != " ":
                self.connector.create_concept(node, synonims=[synonims[node]], child_concepts={}, parent_concepts={}, antonims=[], data={})
        # make all nodes with antonims
        for node in antonims:
            self.log.info("processing antonims of node: " + node)
            if node is not None and node != "" and node != " ":
                self.connector.create_concept(node, synonims=[], child_concepts={}, parent_concepts={}, antonims=[antonims[node]], data={})
        # make all nodes with data
        for node in data:
            self.log.info("processing data of node: " + node)
            if node is not None and node != "" and node != " ":
                self.connector.create_concept(node, data=data[node], synonims=[], child_concepts= {}, parent_concepts={}, antonims=[])

        # update crawler
        self.crawler.update_connector(self.connector)

    def handle_learning(self, utterance):
        self.log.info("learning correct answer")
        if self.debug:
            self.speak("learning correct answer")
            self.speak("Searching wolfram alpha")
        # this is placeholder, always call wolfram, when question type is fully implemented wolfram maybe wont be called
        learned = self.handle_unknown_intent(utterance)

        if not learned:
            self.speak("i dont know the answer")
        return learned
        # TODO ask user questions about unknown nodes, teach skill handles response

    def handle_fallback(self, message):
        # on single utterance intent failure ask user for correct answer
        utterance = message.data["utterance"]
        self.deduce_answer(utterance)

    def handle_multiple_fallback(self, message):
        # on multiple utterance intent failure ask user for correct answer
        utterances = message.data["utterances"]
        for utterance in utterances:
            self.deduce_answer(utterance)

    # questions methods
    def handle_talk_about(self, node, node2, utterance=""):

        # dont talk about "action" node
        if node == "talk" or node == "rant":
            node = node2

        # say what
        talked = self.handle_what_intent(node)
        if not talked:
            # no what ask wolfram
            talked = self.handle_unknown_intent(utterance)

        # get related nodes
        related = self.connector.get_cousins(node)

        if self.debug:
            self.speak("related subjects: " + str(related))
        try:
            # pick one at random
            choice = random.choice(related).lower()
            if self.debug:
                self.speak("chosing related topic: " + choice)
            # talk about it
            more = self.handle_what_intent(choice)
            if not more:
                self.handle_unknown_intent(choice)
        except:
            if self.debug:
                self.speak("could not find related info")
            self.log.info("could not find related info")
        return talked

    def handle_relation(self, center_node, target_node):
        self.crawler.update_connector(self.connector)
        commons = common_this_and_that(center_node, target_node, self.crawler)
        for common in commons:
            self.speak(center_node + " are " + common + " like " + target_node)
        if commons == []:
            self.speak(center_node + " and " + target_node + " have nothing in common")
        return True

    def handle_why(self, center_node, target_node):
        # is this that
        self.crawler.update_connector(self.connector)
        flag = is_this_that(center_node, target_node, self.crawler)
        self.speak("answer to is " + center_node + " a " + target_node + " is " + str(flag))
        if flag:
            # why
            nodes = why_is_this_that(center_node, target_node, self.crawler)
            i = 0
            for node in nodes:
                if node != target_node:
                    self.speak(node + " is " + nodes[i + 1])
                i += 1
        return True

    def handle_how_intent(self, utterance):
        how_to = self.service.adquire(utterance, "wikihow")
        # TODO emit bus message for connector to update node with info
        how_to = how_to["wikihow"]
        # TODO check for empty how to and return false
        # the following how_tos are available
        self.speak("the following how tos are available")
        for how in how_to:
            self.speak(how)
        # TODO create intent tree
        # TODO start selection query
        # TODO speak how to
        return True

    def handle_compare_intent(self, center_node, target_node):
        self.crawler.update_connector(self.connector)
        flag = is_this_that(center_node, target_node, self.crawler)
        self.speak("answer to is " + center_node + " a " + target_node + " is " + str(flag))
        return True

    def handle_unknown_intent(self, utterance):
        # get answer from wolfram alpha
        result = None
        result = self.service.adquire(utterance, "wolfram alpha")

        result = result["wolfram alpha"]
        answer = result["answer"]
        parents = result["parents"]
        synonims = result["synonims"]
        relevant = result["relevant"]
        childs = {}
        antonims = {}
        if self.debug:
            self.speak("new nodes from wolfram alpha answer: " + answer)
            self.speak("parents: " + str(parents))
            self.speak("synonims: " + str(synonims))
            self.speak("relevant: " + str(relevant))
        # TODO load/update nodes
        self.handle_update_connector(relevant, parents, childs, synonims, antonims)
        # say answer to user
        if answer != "no answer":
            self.speak(answer)
            return True
        return False

    def handle_examples_intent(self, node):
        self.crawler.update_connector(self.connector)
        examples = examples_of_this(node, self.crawler)
        for example in examples:
            if example != node:
                self.speak(example + " is an example of " + node)
        if not examples:
            self.speak("i dont know any examples of " + node)
            return False
        else:
            return True

    def handle_what_intent(self, node):
        data = self.connector.get_data(node)
        dbpedia = {}
        wikidata = {}
        wikipedia = {}

        if self.debug:
            self.speak("node data: " + str(data))

        # get data from web
        if data == {}:
            self.log.info("no node data available")
            if self.debug:
                self.speak("seaching dbpedia")
            self.log.info("adquiring dbpedia")
            try:
                dbpedia = self.service.adquire(node, "dbpedia")["dbpedia"][node]
            except:
                if self.debug:
                    self.speak("no results from dbpedia")
                self.log.info("no results from dbpedia")

                if self.debug:
                    self.speak("seaching wikidata")
                self.log.info("adquiring wikidata")
                try:
                    wikidata = self.service.adquire(node, "wikidata")["wikidata"]
                except:
                    if self.debug:
                        self.speak("no results from wikidata")
                    self.log.info("no results from wikidata")

                    if self.debug:
                        self.speak("seaching wikipedia")
                    self.log.info("adquiring wikipedia")
                    try:
                        wikipedia = self.service.adquire(node, "wikipedia")["wikipedia"]
                    except:
                        if self.debug:
                            self.speak("no results from wikipedia")
                        self.log.info("no results from wikipedia")

           # debug available data

            if self.debug:
                self.speak("dbpedia data: " + str(dbpedia))
                self.speak("wikidata data: " + str(wikidata))
                self.speak("wikipedia data: " + str(wikipedia))

        # update data from web
        try:
            # dbpedia parents are handled in pre-processing / curiosity
            abstract = dbpedia["page_info"]["abstract"]
            data["abstract"] = abstract
            self.connector.add_data(node, "abstract", abstract)
            pic = dbpedia["page_info"]["picture"]
            self.connector.add_data(node, "pic", pic)
            links = dbpedia["page_info"]["external_links"]
            self.connector.add_data(node, "links", links)
            cousins = dbpedia["page_info"]["related_subjects"]
            concepts = self.connector.get_concept_names()
            for cousin in cousins:
                if cousin not in concepts:
                    if self.debug:
                        self.speak("creating concept: " + cousin)
                    self.connector.create_concept(new_concept_name=cousin.lower(), data={}, child_concepts={},
                                              parent_concepts={}, synonims=[], antonims=[])
                if cousin not in self.connector.get_cousins(node):
                    if self.debug:
                        self.speak("adding cousin: " + cousin + " to concept: " + node)
                    self.log.info("adding cousin: " + cousin + " to concept: " + node)
                    self.connector.add_cousin(node, cousin.lower())
        except:
            self.log.error("no dbpedia for " + node)
            try:
                # TODO all fields
                description = wikidata["description"]
                data["description"] = description
                self.connector.add_data(node, "description", description)
            except:
                self.log.error("no wikidata for " + node)
            try:
                # TODO all fields
                summary = wikipedia["summary"]
                data["summary"] = summary
                self.connector.add_data(node, "summary", summary)
                description = wikipedia["description"]
                data["description"] = description
                self.connector.add_data(node, "description", description)
            except:
                self.log.error("no wikipedia for " + node)

        self.crawler.update_connector(self.connector)

        # read node data
        try:
            abstract = data["abstract"]
            if abstract != "":
                self.speak(abstract)
                return True
        except:
            pass
        try:
            description = data["description"]
            if description != "":
                self.speak(description)
                return True
        except:
            pass
        try:
            summary = data["summary"]
            if summary != "":
                self.speak(summary)
                return True
        except:
            pass

        # TODO use intent tree to give interactive dialog suggesting more info
        # self.speak("Do you want examples of " + node)
        # activate yes intent
        # use converse method to disable or do something
        return False

    def handle_who_intent(self, node):
        self.crawler.update_connector(self.connector)
        return False

    def handle_when_intent(self, node):
        self.crawler.update_connector(self.connector)
        return False

    def handle_where_intent(self, node):
        self.crawler.update_connector(self.connector)
        return False

    def handle_which_intent(self, node):
        self.crawler.update_connector(self.connector)
        return False

    def handle_whose_intent(self, node):
        self.crawler.update_connector(self.connector)
        return False

    # feedback
    def handle_incorrect_answer(self):
        # create nodes / connections for right answer
        #self.last_question = ""
        #self.last_question_type = ""
        #self.last_center = ""
        #self.last_target = ""
        self.speak_dialog("wrong_answer")

    def feedback(self, message):
        feedback = message.data["feedback"]
        # check if previously answered a question
        if feedback == "negative" and self.answered:
            # wrong answer was given, react to negative feedback
            self.handle_incorrect_answer()
        if feedback == "negative" and not self.answered:
            # no apparent reason for negative feedback
            self.speak_dialog("wrong_answer_confused")

    def stop(self):
        pass

def create_skill():
    return LilacsCoreSkill()

