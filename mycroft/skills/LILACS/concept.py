from mycroft.util.crawl_log import getLogger as CrawlLogger
from mycroft.util.log import getLogger
import random
import math

__authors__ = ["jarbas", "heinzschmidt"]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))

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

    def __init__(self, name, data={}, parent_concepts={},
        child_concepts={}, synonims=[], antonims=[], cousins = [],
        spawns = [], spawned_by = [], consumes = [], consumed_by = [],
        parts = [], part_off=[], type="info"):
        self.name = name
        self.type = type
        self.data = data
        self.connections = {}
        self.connections.setdefault("parents", parent_concepts)
        self.connections.setdefault("childs", child_concepts)
        self.connections.setdefault("synonims", synonims)
        self.connections.setdefault("antonims", antonims)
        self.connections.setdefault("cousins", cousins)
        self.connections.setdefault("spawns", spawns)
        self.connections.setdefault("spawned_by", spawned_by)
        self.connections.setdefault("consumes", consumes)
        self.connections.setdefault("consumed_by", consumed_by)
        self.connections.setdefault("parts", parts)
        self.connections.setdefault("part_off", part_off)

    def get_parents(self):
        return self.connections["parents"];

    def get_childs(self):
        return self.connections["childs"];

    def get_cousins(self):
        return self.connections["cousins"];

    def get_consumes(self):
        return self.connections["consumes"];

    def get_consumed_by(self):
        return self.connections["consumed_by"];

    def get_spawn(self):
        return self.connections["spawns"];

    def get_spawned_by(self):
        return self.connections["spawned_by"];

    def get_parts(self):
        return self.connections["parts"];

    def get_part_off(self):
        return self.connections["part_off"];

    def get_synonims(self):
        return self.connections["synonims"];

    def get_antonims(self):
        return self.connections["antonims"];

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

    def __init__(self, concepts = {}):
        self.concepts = concepts
        self.logger = getLogger("ConceptConnector")

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
            self.logger.info("### Concept found: " + str(concept_name))

            for parent in concept.get_parents():
                if parent not in self.get_parents(concept_name):
                    self.logger.info(("Adding parent node: " + parent))
                    self.concepts[concept_name].add_parent(parent, gen=concept.get_parents()[parent])
            for child in concept.connections["childs"]:
                if child not in self.get_childs(concept_name):
                    self.concepts[concept_name].add_child(child, gen=concept.get_childs()[child])
            for antonim in concept.connections["antonims"]:
                if antonim not in self.concepts[concept_name].antonims:
                    self.concepts[concept_name].connections["antonims"].add_antonim(antonim)
            for synonim in concept.connections["synonims"]:
                if synonim not in self.concepts[concept_name].synonims:
                    self.concepts[concept_name].connections["synonims"].add_synonim(synonim)

        else:
            self.concepts.setdefault(concept_name, concept)

    def remove_concept(self, concept_name):
        self.concepts.pop(concept_name)

    def get_childs(self, concept_name):
        return self.concepts[concept_name].get_childs()

    def get_parents(self, concept_name):
        return self.concepts[concept_name].get_parents()

    def get_antonims(self, concept_name):
        return self.concepts[concept_name].get_antonims()

    def get_synonims(self, concept_name):
        return self.concepts[concept_name].get_synonims()

    def create_concept(self, new_concept_name, data={},
                           child_concepts={}, parent_concepts={}, synonims=[], antonims=[]):

        self.logger.info(("### Creating new concept: " + str(new_concept_name)))

        # safe - checking
        if new_concept_name in parent_concepts:
            parent_concepts.pop(new_concept_name)
        if new_concept_name in child_concepts:
            child_concepts.pop(new_concept_name)


        # handle new concept
        concept = ConceptNode(name=new_concept_name, data=data, child_concepts=child_concepts, parent_concepts=parent_concepts,
                              synonims=synonims, antonims=antonims)
        self.logger.info(("### New ConceptNode created."))

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



class ConceptCrawler():
    def __init__(self, depth=20, concept_connector=None):
        # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/9
        self.logger = CrawlLogger("Crawler", "Drunk")
        # concept database
        self.concept_db = concept_connector
        if self.concept_db is None:
            self.concept_db = ConceptConnector(getLogger("ConceptConnector"))
        # crawl depth
        self.depth = depth
        # crawl path
        self.crawl_path = []
        # crawled antonims
        self.do_not_crawl = []
        # nodes we left behind without checking
        self.uncrawled = []
        # nodes we already checked
        self.crawled = []
        # count visits to each node
        self.visits = {}
        #
        self.short_path = []

    def find_all_paths(self, center_node, target_node, path=[], direction="parents"):
        path = path + [center_node]
        self.logger.info("Current Node: " + center_node)
        self.visits[center_node] += 1
        if center_node == target_node:
            self.logger.info("path found from " + path[0] + " to " + target_node)
            self.logger.info(path)
            return [path]

        if center_node not in self.concept_db.concepts:
            return []

        paths = []

        self.logger.info("getting " + direction)
        if direction == "parents":
            nodes = self.concept_db.get_parents(center_node)
        elif direction == "childs":
            nodes = self.concept_db.get_childs(center_node)
        else:
            self.logger.error("Invalid crawl direction")
            return None

        for node in nodes:
            if node not in path:
                newpaths = self.find_all_paths(node, target_node, path, direction)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

    def find_shortest_path(self, center_node, target_node, path=[], direction="parents"):
        self.logger = CrawlLogger("Crawler", "Explorer")
        self.logger.info("finding all paths from " + center_node + " to " + target_node)
        paths = self.find_all_paths(center_node, target_node, direction=direction)
        shortest = None
        for newpath in paths:
            if not shortest or len(newpath) < len(shortest):
                shortest = newpath
        self.logger.info("shortest path is: " + str(shortest))
        return shortest

    def find_minimum_node_distance(self, center_node, target_node):
        return len(self.find_shortest_path(center_node, target_node))

    def get_total_crawl_distance(self):
        return len(self.crawled)

    def get_crawl_path_distance(self):
        return len(self.crawl_path
                   )

    def mark_as_crawled(self, node):
        self.logger.info("Marking node as crawled: " + node)
        # remove current node from uncrawled nodes list
        i = 0
        for uncrawled_node in self.uncrawled:
            if uncrawled_node == node:
                self.uncrawled.pop(i)
            i += 1
        # add current node to crawled list
        if node not in self.crawled:
            self.crawled.append(node)

    def choose_next_node(self, node, direction="parents"):
        # when choosing the next node we have to think about what matters more
        # - checking child or parent?
        # - does node have synonims?
        # - is any of the connected nodes blacklisted in this crawl (antonim)?
        # - choose stronger connections preferably
        # - number of times we visited this node
        if node is None:
            return node

        # keep count of visits to this node
        if node in self.visits:
            self.visits[node] += 1
        else:
            self.visits[node] = 1

        self.logger.info("Number of visits to this node: " + str(self.visits[node]))

        # add current node to crawl path
        self.crawl_path.append(node)

        self.mark_as_crawled(node)

        # are we checking parents or childs?
        if direction == "parents":
            nodes = self.concept_db.get_parents(node)
            # check if node as synonims
            synonims = self.concept_db.get_synonims(node)
            for synonim in synonims:
                # get connections of these synonims also
                self.logger.info("found synonim: " + synonim)
                self.logger.info("adding synonim connections to crawl list")
                nodes += self.concept_db.get_parents(synonim)
        elif direction == "childs":
            nodes = self.concept_db.get_childs(node)
            # check if node as synonims
            synonims = self.concept_db.get_synonims(node)
            for synonim in synonims:
                # get connections of these synonims also
                self.logger.info("found synonim: " + synonim)
                self.logger.info("adding synonim connections to crawl list")
                nodes += self.concept_db.get_childs(synonim)
        else:
            self.logger.error("Invalid crawl direction")
            return None

        # if no connections found return
        if len(nodes) == 0:
            self.logger.info(node + " doesn't have any " + direction + " connection")
            return None

        # add these nodes to "nodes to crawl"
        for node in dict(nodes):
            self.uncrawled.append(node)
            # add all antonims from these nodes to do no crawl
            for antonim in self.concept_db.get_antonims(node):
                self.do_not_crawl.append(antonim)
                self.logger.info("blacklisting node " + antonim + " because it is an antonim of: " + node)
            # remove any node we are not supposed to crawl
            if node in self.do_not_crawl:
                self.logger.info("we are in a blacklisted node: " + node)
                nodes.pop(node)

        # create a weighted list giving preference


        new_weights = {}
        for node in nodes:
            # turn all values into a value between 0 and 1
            # multiply by 100
            # smaller values are more important
            new_weights[node] = int(100 - sigmoid(nodes[node]) * 100)
        self.logger.info("next node weights are: " + str(new_weights))

        list = [k for k in new_weights for dummy in range(new_weights[k])]
        if list == []:
            next_node = None
        else:
            # choose a node to crawl next
            next_node = random.choice(list)
        return next_node

    def reset_visit_counter(self):
        # visit counter at zero
        for node in self.concept_db.concepts:
            self.visits[node] = 0

    def drunk_crawl(self, center_node, target_node, direction="parents"):
        # reset variables
        self.logger = CrawlLogger("Crawler", "Drunk")
        # crawl path
        self.crawl_path = []
        # crawled antonims
        self.do_not_crawl = []
        # nodes we left behind without checking
        self.uncrawled = []
        # nodes we already checked
        self.crawled = []
        # count visits to each node
        self.visits = {}
        # start at center node
        self.logger.info("start node: " + center_node)
        self.logger.info("target node: " + target_node)
        next_node = self.choose_next_node(center_node, direction)
        crawl_depth = 1
        while True:
            # check if we found answer
            if target_node in self.crawled:
                self.logger.info("Found target node")
                return True
            if next_node is None:
                # choose next node
                if len(self.uncrawled) == 0:
                    self.logger.info("No more nodes to crawl")
                    #no more nodes to crawl
                    return False
                # reached a dead end, pic next unchecked node
                # chose last uncrawled node (keep on this path)
                next_node = self.uncrawled[-1]
                # check crawl_depth threshold
                if crawl_depth >= self.depth:
                    # do not crawl further
                    self.logger.info("Maximum crawl depth reached: " + str(crawl_depth))
                    return False
            self.logger.info( "next: " + next_node)
            self.logger.info( "depth: " + str(crawl_depth))
            # see if we already crawled this
            if next_node in self.crawled:
                self.logger.info("crawling this node again: " + next_node)
                # increase visit counter
                self.visits[next_node] += 1
                self.logger.info("number of visits: " + str(self.visits[next_node]))
                # add to crawl path
                self.crawl_path.append(next_node)
                # remove fom uncrawled list
                i = 0
                for node in self.uncrawled:
                    if node == next_node:
                        self.logger.info("removing node from uncrawled node list: " + node)
                        self.uncrawled.pop(i)
                    i += 1
                # chose another to crawl
                next_node = None
            # crawl next node
            self.logger.info("choosing next node")
            next_node = self.choose_next_node(next_node, direction)
            self.logger.info("crawled nodes: " + str(self.crawled))
            # print "crawl_path: " + str(self.crawl_path)
            self.logger.info("uncrawled nodes: " + str(self.uncrawled))
            crawl_depth += 1  # went further

    def explorer_crawl(self, center_node, target_node, direction="parents"):
        self.logger = CrawlLogger("Crawler", "Explorer")
        self.uncrawled = []  # none
        self.do_not_crawl = []  # none
        self.reset_visit_counter()
        self.crawled = []  # all nodes
        for node in self.concept_db.concepts:
            self.crawled.append(node)
        self.crawl_path = self.find_shortest_path(center_node, target_node, direction=direction)




