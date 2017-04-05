import json
from os.path import join, dirname

__authors__ = ["jarbas", "heinzschmidt"]

class ConceptNode():
    def __init__(self, name, data={}, parent_concepts={},
        child_concepts={}, synonims=[], antonims=[]):
        self.name = name
        self.synonims = synonims
        self.antonims = antonims
        self.parent_concepts = parent_concepts
        self.child_concepts = child_concepts
        self.data = {}

    def add_synonim(self, synonim):
        if synonim not in self.synonims:
            self.synonims.append(synonim)

    def add_data(self, key, data={}):
        if key in self.data:
            self.data[key] = data
        else:
            self.data.setdefault(key, data)

    def add_parent(self, parent_name, gen = 1):
        if parent_name not in self.parent_concepts and parent_name != self.name:
            self.parent_concepts.setdefault(parent_name, gen)
        elif parent_name in self.parent_concepts and parent_name != self.name:
            self.parent_concepts[parent_name]=gen

    def add_child(self, child_name, gen=1):
        if child_name not in self.child_concepts and child_name != self.name:
            self.child_concepts.setdefault(child_name, gen)
        elif child_name in self.child_concepts and child_name != self.name:
            self.child_concepts[child_name]=gen

    def remove_synonim(self, synonim):
        i = 0
        for name in self.synonims:
            if name == synonim:
                self.child_concepts.pop(i)
                return
            i += 1

    def remove_data(self, key):
        self.data.pop(key)

    def remove_parent(self, parent_name):
        self.parent_concepts.pop(parent_name)

    def remove_child(self, child_name):
        self.child_concepts.pop(child_name)


class ConceptCreator():
    def __init__(self, logger,  concepts = {}):
        self.concepts = concepts
        self.logger = logger

    def add_concept(self, concept_name, concept):
        if concept_name in self.concepts:
            #  merge fields
            for parent in concept.parent_concepts:
                if parent not in self.get_parents(concept_name):
                    self.concepts[concept_name].add_parent(parent, gen= concept.parent_concepts[parent])
            for child in concept.child_concepts:
                if child not in self.get_childs(concept_name):
                    self.concepts[concept_name].add_child(child, gen= concept.child_concepts[child])
            for antonim in concept.antonims:
                if antonim not in self.concepts[concept_name].antonims:
                    self.concepts[concept_name].antonims.add_antonim(antonim)
            for synonim in concept.synonims:
                if synonim not in self.concepts[concept_name].synonims:
                    self.concepts[concept_name].synonims.add_synonim(synonim)
        else:
            self.concepts.setdefault(concept_name, concept)

    def remove_concept(self, concept_name):
        self.concepts.pop(concept_name)

    def get_childs(self, concept_name):
        return self.concepts[concept_name].child_concepts

    def get_parents(self, concept_name):
        return self.concepts[concept_name].parent_concepts

    def create_concept(self, new_concept_name, data={},
                       child_concepts={}, parent_concepts={}, synonims=[], antonims=[], gen =0):
        self.logger.info("processing concept " + new_concept_name)

        # handle new concept
        self.logger.info("creating node for " + new_concept_name)
        concept = ConceptNode(new_concept_name, data, parent_concepts, child_concepts, synonims, antonims)
        self.add_concept(new_concept_name, concept)

        # handle parent concepts
        for concept_name in dict(parent_concepts):
            self.logger.info("processing parent: " + concept_name)

            # create parent if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("parent doesnt exit, creating")
                concept = ConceptNode(concept_name, child_concepts={new_concept_name: gen})
                self.add_concept(concept_name, concept)
            # add child
            if new_concept_name not in self.get_childs(concept_name):
                self.logger.info("adding child to parent")
                self.concepts[concept_name].add_child(new_concept_name, gen)

            # add parents of parents (if jon is human and humans are animals, jon is an animal)
            for grandpa_concept_name in self.get_parents(concept_name):
                self.logger.info("processing grand_parent: " + grandpa_concept_name)
                self.create_concept(grandpa_concept_name, child_concepts={new_concept_name: gen + 1 }, gen=gen + 1)

        # handle child concepts
        for concept_name in child_concepts:
            self.logger.info("processing child: " + concept_name)
            # create child if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating child")
                concept = ConceptNode(concept_name, parent_concepts={new_concept_name: gen})
                self.add_concept(concept_name, concept)

            # add parent to child if it exists
            if new_concept_name not in self.get_parents(concept_name):
                self.logger.info("adding parent to child")
                self.concepts[concept_name].add_parent(new_concept_name, gen)

            # add as parent of grandchilds also
            for grandchild_concept_name in self.get_childs(concept_name):
                self.logger.info("processing grand_child: " + grandchild_concept_name)
                # self.create_concept(grandpa_concept_name, child_concepts={new_concept_name: gen + 2}, gen = gen +2)
                # create child if it doesnt exist
                if grandchild_concept_name not in self.concepts:
                    self.logger.info("grand_child doesnt exist, creating ")
                    concept = ConceptNode(grandchild_concept_name, parent_concepts={new_concept_name: gen + 2})
                    self.add_concept(grandchild_concept_name, concept)
                # add grand_parent
                self.logger.info("adding grand_parent")
                self.concepts[grandchild_concept_name].add_parent(new_concept_name, gen + 2)



class ConceptStorage():

    _dataStorageType = ""
    _dataStorageUser = ""
    _dataStoragePass = ""
    _dataStorageDB = ""
    _dataConnection = None
    _dataConnStatus = 0
    _dataJSON = None
    _storagepath = ""

    def __init__(self, storagepath, storagetype="json", database="lilacstorage.db"):
        self._storagepath = storagepath
        self._dataStorageType = storagetype
        self._dataStorageDB = database
        self.datastore_connect()

    def datastore_connect(self):
        if(self._dataStorageType == "sqllite3"):
            """try:
                self._dataConnection = sqllite3.connect(self._dataStorageDB)
                self._dataConnStatus = 1
            except Exception as sqlerr:
                # log something
                print(("Database connection failed" + str(sqlerr)))
                self._dataConnStatus = 0
            """
        elif(self._dataStorageType == "json"):
            with open(self._storagepath + self._dataStorageDB)\
             as datastore:
                self._dataJSON = json.load(datastore)

            if(self._dataJSON):
                self._dataConnStatus = 1
            else:
                self._dataConnStatus = 0

    def getNodeDataDictionary(self, conceptname="cow"):
        returnVal = {}
        if(self._dataConnStatus == 1):
            for p in self._dataJSON[conceptname]:
                returnVal["data_dict"] = str(p["data_dict"])
        return returnVal

    def getNodeParent(self, conceptname="cow", generation=None):
        returnVal = {}
        if(self._dataConnStatus == 1):
            for node in self._dataJSON[conceptname]:
                if(generation is None):
                    for parent in node["parents"]:
                        returnVal = parent
                elif(generation <= len(node["parents"])):
                    for parent in node["parents"]:
                        if parent[str(generation)]:
                            returnVal = parent[str(generation)]
        return returnVal

    def getNodeChildren(self, conceptname="cow", generation=None):
        returnVal = {}
        if(self._dataConnStatus == 1):
            for node in self._dataJSON[conceptname]:
                if(generation is None):
                    for child in node["children"]:
                        returnVal = child
                elif(generation <= len(node["children"])):
                    for child in node["children"]:
                        if child[str(generation)]:
                            returnVal = child[str(generation)]
        return returnVal

    def getNodeSynonymn(self, conceptname="cow", generation=None):
        returnVal = {}
        if(self._dataConnStatus == 1):
            for node in self._dataJSON[conceptname]:
                if(generation is None):
                    for synonymn in node["synonymns"]:
                        returnVal = synonymn
                elif(generation <= len(node["synonymns"])):
                    for synonymn in node["synonymns"]:
                        if synonymn[str(generation)]:
                            returnVal = synonymn[str(generation)]
            return returnVal

    def getNodeAntonymn(self, conceptname="cow", generation=None):
        returnVal = {}
        if(self._dataConnStatus == 1):
            for node in self._dataJSON[conceptname]:
                if(generation is None):
                    for synonymn in node["antonymns"]:
                        returnVal = synonymn
                elif(generation <= len(node["antonymns"])):
                    for synonymn in node["antonymns"]:
                        if synonymn[str(generation)]:
                            returnVal = synonymn[str(generation)]
            return returnVal

    def getNodeLastUpdate(self, conceptname="cow"):
        returnVal = {}
        if(self._dataConnStatus == 1):
            for p in self._dataJSON[conceptname]:
                returnVal["last_update"] = str(p["last_update"])
        return returnVal


