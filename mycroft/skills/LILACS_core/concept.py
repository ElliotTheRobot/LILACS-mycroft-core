from mycroft.util.log import getLogger


__authors__ = ["jarbas", "heinzschmidt"]


class ConceptNode():
    ''' 
    Node:
       name:
       type: "informational"   <- all discussed nodes so far are informational
       Connections:
           synonims: []  <- is the same as
           antonims: [] <- can never be related to
           parents: []  <- is an instance of
           childs: [] <- can have the following instances 
           cousins: [] <- somewhat related subjects 
           spawns: []  <- what comes from this?
           spawned_by: [] <- where does this come from?
           consumes: [] <- what does this need/spend ?
           consumed_by: []  <- what consumes this?
           parts : [ ] <- what smaller nodes can this be divided into?
           part_off: [ ] <- what can be made out of this?
       Data:
            description: wikidata description_field
            abstract: dbpedia abstract
            summary: wikipedia_summary
            pics: [ wikipedia pic, dbpedia pic ]
            infobox: {wikipedia infobox}
            wikidata: {wikidata_dict}
            props: [wikidata_properties] <- if we can parse this appropriatly we can make connections
            links: [ wikipedia link, dbpedia link  ]
            external_links[ suggested links from dbpedia]
    '''

    def __init__(self, name, data=None, parent_concepts=None,
        child_concepts=None, synonims=None, antonims=None, cousins = None,
        spawns = None, spawned_by = None, consumes = None, consumed_by = None,
        parts = None, part_off=None, type="info"):
        self.name = name
        self.type = type
        self.data = data
        self.connections = {}
        if parent_concepts is not None:
            self.connections.setdefault("parents", parent_concepts)
        else:
            self.connections.setdefault("parents", {})
        if child_concepts is not None:
            self.connections.setdefault("childs", child_concepts)
        else:
            self.connections.setdefault("childs", {})
        if synonims is not None:
            self.connections.setdefault("synonims", synonims)
        else:
            self.connections.setdefault("synonims", [])
        if antonims is not None:
            self.connections.setdefault("antonims", antonims)
        else:
            self.connections.setdefault("antonims", [])
        if cousins is not None:
            self.connections.setdefault("cousins", cousins)
        else:
            self.connections.setdefault("cousins", [])
        if spawns is not None:
            self.connections.setdefault("spawns", spawns)
        else:
            self.connections.setdefault("spawns", [])
        if spawned_by is not None:
            self.connections.setdefault("spawned_by", spawned_by)
        else:
            self.connections.setdefault("spawned_by", [])
        if consumes is not None:
            self.connections.setdefault("consumes", consumes)
        else:
            self.connections.setdefault("consumes", [])
        if consumed_by is not None:
            self.connections.setdefault("consumed_by", consumed_by)
        else:
            self.connections.setdefault("consumed_by", [])
        if parts is not None:
            self.connections.setdefault("parts", parts)
        else:
            self.connections.setdefault("parts", [])
        if part_off is not None:
            self.connections.setdefault("part_off", part_off)
        else:
            self.connections.setdefault("part_off", [])

    def get_parents(self):
        return self.connections["parents"]

    def get_childs(self):
        return self.connections["childs"]

    def get_cousins(self):
        return self.connections["cousins"]

    def get_consumes(self):
        return self.connections["consumes"]

    def get_consumed_by(self):
        return self.connections["consumed_by"]

    def get_spawn(self):
        return self.connections["spawns"]

    def get_spawned_by(self):
        return self.connections["spawned_by"]

    def get_parts(self):
        return self.connections["parts"]

    def get_part_off(self):
        return self.connections["part_off"]

    def get_synonims(self):
        return self.connections["synonims"]

    def get_antonims(self):
        return self.connections["antonims"]

    def get_data(self):
        return self.data

    def add_synonim(self, synonim):
        if synonim not in self.connections["synonims"]:
            self.connections["synonims"].append(synonim)

    def add_antonim(self, antonim):
        if antonim not in self.connections["antonims"]:
            self.connections["antonims"].append(antonim)

    def add_data(self, key, data={}):
        if key in self.data:
            self.data[key] = data
        else:
            self.data.setdefault(key, data)

    def add_parent(self, parent_name, gen = 1, update = True):

        # a node cannot be a parent  of itself
        if parent_name == self.name:
            return

        # a node cannot be a parent and a child (would it make sense in some corner case?)
        if parent_name in self.connections["childs"]:
            return

        if parent_name not in self.connections["parents"]:
            self.connections["parents"].setdefault(parent_name, gen)
        elif parent_name in self.connections["parents"] and update:
            self.connections["parents"][parent_name] = gen

    def add_child(self, child_name, gen=1, update = True):
        # a node cannot be a child of itself
        if child_name == self.name:
            return

        if child_name in self.connections["parents"]:
            return

        if child_name not in self.connections["childs"]:
            self.connections["childs"].setdefault(child_name, gen)
        elif child_name in self.connections["childs"] and update:
            self.connections["childs"][child_name] = gen

    def add_cousin(self, cousin):
        if cousin not in self.connections["cousins"]:
            self.connections["cousins"].append(cousin)

    def add_spawn(self, spawn):
        if spawn not in self.connections["spawns"]:
            self.connections["spawns"].append(spawn)

    def add_spawned_by(self, spawned_by):
        if spawned_by not in self.connections["spawned_by"]:
            self.connections["spawned_by"].append(spawned_by)

    def add_consumes(self, consumes):
        if consumes not in self.connections["consumes"]:
            self.connections["consumes"].append(consumes)

    def add_consumed_by(self, consumed_by):
        if consumed_by not in self.connections["consumed_by"]:
            self.connections["consumed_by"].append(consumed_by)

    def add_part(self, part):
        if part not in self.connections["parts"]:
            self.connections["parts"].append(part)

    def add_part_off(self, part_off):
        if part_off not in self.connections["part_off"]:
            self.connections["part_off"].append(part_off)

    def remove_synonim(self, synonim):
        i = 0
        for name in self.connections["synonims"]:
            if name == synonim:
                self.connections["synonims"].pop(i)
                return
            i += 1

    def remove_antonim(self, antonim):
        i = 0
        for name in self.connections["antonims"]:
            if name == antonim:
                self.connections["antonims"].pop(i)
                return
            i += 1

    def remove_cousin(self, cousin):
        i = 0
        for name in self.connections["cousins"]:
            if name == cousin:
                self.connections["cousins"].pop(i)
                return
            i += 1

    def remove_part(self, part):
        i = 0
        for name in self.connections["parts"]:
            if name == part:
                self.connections["parts"].pop(i)
                return
            i += 1

    def remove_part_off(self, part_off):
        i = 0
        for name in self.connections["part_off"]:
            if name == part_off:
                self.connections["part_off"].pop(i)
                return
            i += 1

    def remove_consumes(self, consumes):
        i = 0
        for name in self.connections["consumes"]:
            if name == consumes:
                self.connections["consumes"].pop(i)
                return
            i += 1

    def remove_consumed_by(self, consumed_by):
        i = 0
        for name in self.connections["consumed_by"]:
            if name == consumed_by:
                self.connections["consumed_by"].pop(i)
                return
            i += 1

    def remove_spawns(self, spawn):
        i = 0
        for name in self.connections["spawns"]:
            if name == spawn:
                self.connections["spawns"].pop(i)
                return
            i += 1

    def remove_spawned_by(self, spawned_by):
        i = 0
        for name in self.connections["spawned_by"]:
            if name == spawned_by:
                self.connections["spawned_by"].pop(i)
                return
            i += 1

    def remove_data(self, key):
        self.data.pop(key)

    def remove_parent(self, parent_name):
        self.connections["parents"].pop(parent_name)

    def remove_child(self, child_name):
        self.connections["childs"].pop(child_name)


class ConceptConnector():

    def __init__(self, concepts = {}, emitter=None):
        self.concepts = concepts
        self.logger = getLogger("ConceptConnector")
        self.emitter = emitter
        self.emitter.on("new_node", self.new_node)

    def new_node(self, message):
        # create node signaled from outside
        node_name = message.data["node_name"]
        p = message.data["parents"]
        parents = {}
        for parent in p:
            parents.setdefault(parent, 7)
        c = message.data["childs"]
        childs = {}
        for child in c:
            childs.setdefault(child, 7)
        synonims = message.data["synonims"]
        antonims = message.data["antonims"]
        data = message.data["data"]
        self.create_concept(new_concept_name=node_name, parent_concepts=parents, child_concepts=childs, synonims=synonims, antonims=antonims, data=data)
        # TODO other fields
        # TODO if configured gather node info from knowledge service?
        # TODO update node in storage

    def get_concept_names(self):
        concepts = []
        for name in self.concepts:
            concepts.append(name)
        return concepts

    def get_concepts(self):
        return self.concepts

    def add_concept(self, concept_name, concept):
        if concept_name in self.concepts:
            #  merge fields
            for parent in concept.get_parents():
                if parent not in self.get_parents(concept_name):
                    self.logger.info(("adding parent node: " + parent))
                    self.concepts[concept_name].add_parent(parent, gen=concept.get_parents()[parent])
            for child in concept.connections["childs"]:
                if child not in self.get_childs(concept_name):
                    self.logger.info("adding child node: " + str(child))
                    self.concepts[concept_name].add_child(child, gen=concept.get_childs()[child])
            for antonim in concept.get_antonims():
                if antonim not in self.concepts[concept_name].get_antonims():
                    self.logger.info("adding antonim: " + str(antonim))
                    self.concepts[concept_name].add_antonim(antonim)
            for synonim in concept.get_synonims():
                if synonim not in self.concepts[concept_name].get_synonims():
                    self.logger.info("adding synonim: " + str(synonim))
                    self.concepts[concept_name].add_synonim(synonim)


        else:
            self.concepts.setdefault(concept_name, concept)

    def remove_concept(self, concept_name):
        self.concepts.pop(concept_name)

    def get_data(self, concept_name):
        return self.concepts[concept_name].get_data()

    def add_data(self, concept_name, key, data={}):
        self.concepts[concept_name].add_data(key, data)

    def get_childs(self, concept_name):
        return self.concepts[concept_name].get_childs()

    def add_child(self, concept_name, child):
        self.concepts[concept_name].add_child(child)

    def get_parents(self, concept_name):
        return self.concepts[concept_name].get_parents()

    def add_parent(self, concept_name, parent):
        self.concepts[concept_name].add_parent(parent)

    def get_antonims(self, concept_name):
        return self.concepts[concept_name].get_antonims()

    def add_antonim(self, concept_name, antonim):
        self.concepts[concept_name].add_antonim(antonim)

    def get_synonims(self, concept_name):
        return self.concepts[concept_name].get_synonims()

    def add_synonim(self, concept_name, synonim):
        self.concepts[concept_name].add_synonim(synonim)

    def get_cousins(self, concept_name):
        return self.concepts[concept_name].get_cousins()

    def add_cousin(self, concept_name, cousin):
        self.logger.info("adding cousin: " + cousin + " to concept: " + concept_name)
        self.concepts[concept_name].add_cousin(cousin)

    def get_parts(self, concept_name):
        return self.concepts[concept_name].get_parts()

    def add_part(self, concept_name, part):
        self.concepts[concept_name].add_part(part)

    def get_part_off(self, concept_name):
        return self.concepts[concept_name].get_part_off()

    def add_part_off(self, concept_name, part_off):
        self.concepts[concept_name].add_part_off(part_off)

    def get_spawn(self, concept_name):
        return self.concepts[concept_name].get_spawn()

    def add_spawn(self, concept_name, spawn):
        self.concepts[concept_name].add_spawn(spawn)

    def get_spawned_by(self, concept_name):
        return self.concepts[concept_name].get_spawned_by()

    def add_spawned_by(self, concept_name, spawned_by):
        self.concepts[concept_name].add_spawned_by(spawned_by)

    def get_consumes(self, concept_name):
        return self.concepts[concept_name].get_consumes()

    def add_consumes(self, concept_name, consumes):
        self.concepts[concept_name].add_consumes(consumes)

    def get_consumed_by(self, concept_name):
        return self.concepts[concept_name].get_consumed_by()

    def add_consumed_by(self, concept_name, consumed_by):
        self.concepts[concept_name].add_consumed_by(consumed_by)

    def create_concept(self, new_concept_name, data={},
                           child_concepts={}, parent_concepts={}, synonims=[], antonims=[]):

        # safe - checking
        if new_concept_name in parent_concepts:
            parent_concepts.pop(new_concept_name)
        if new_concept_name in child_concepts:
            child_concepts.pop(new_concept_name)

        if new_concept_name not in self.concepts:
            self.logger.info("creating concept " + new_concept_name)
        else:
            self.logger.info("updating concept " + new_concept_name)
        # handle new concept
        concept = ConceptNode(name=new_concept_name, data=data, child_concepts=child_concepts, parent_concepts=parent_concepts,
                              synonims=synonims, antonims=antonims)

        self.add_concept(new_concept_name, concept)

        # handle parent concepts
        for concept_name in parent_concepts:
            self.logger.info("checking if parent node exists: " + concept_name)
            gen = parent_concepts[concept_name]
            # create parent if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name )
                concept = ConceptNode(concept_name, data={}, child_concepts={}, parent_concepts={}, synonims=[], antonims=[])
                self.add_concept(concept_name, concept)
            # add child to parent
            self.logger.info("adding child: " + new_concept_name + " to parent: " + concept_name)
            self.concepts[concept_name].add_child(new_concept_name, gen=gen)

        # handle child concepts
        for concept_name in child_concepts:
            self.logger.info("checking if child node exists: " + concept_name)
            gen = child_concepts[concept_name]
            # create child if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name)
                concept = ConceptNode(concept_name, data={}, child_concepts={}, parent_concepts={}, synonims=[], antonims=[])
                self.add_concept(concept_name, concept)
            #add parent to child
            self.logger.info("adding parent: " + new_concept_name + " to child: " + concept_name)
            self.concepts[concept_name].add_parent(new_concept_name, gen=gen)

        # handle synonims
        for concept_name in synonims:
            self.logger.info("checking if synonim exists: " + concept_name)
            # create synonim if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name)
                concept = ConceptNode(concept_name, data={}, child_concepts={}, parent_concepts={}, synonims=[],
                                      antonims=[])
                self.add_concept(concept_name, concept)
            # add synonim to synonim
            self.logger.info("adding synonim: " + new_concept_name + " to concept: " + concept_name)
            self.concepts[concept_name].add_synonim(new_concept_name)

        # handle antonims
        for concept_name in antonims:
            self.logger.info("checking if antonim exists: " + concept_name)
            # create synonim if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name)
                concept = ConceptNode(concept_name, data={}, child_concepts={}, parent_concepts={}, synonims=[],
                                      antonims=[])
                self.add_concept(concept_name, concept)
            # add antonim to antonim
            self.logger.info("adding antonim: " + new_concept_name + " to concept: " + concept_name)
            self.concepts[concept_name].add_antonim(new_concept_name)
