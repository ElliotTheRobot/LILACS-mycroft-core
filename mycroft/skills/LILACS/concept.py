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

    def add_parent(self, parent_name, gen = 1, update = True):

        # a node cannot be a parent  of itself
        if parent_name == self.name:
            return

        # a node cannot be a parent and a child (would it make sense in some corner case?)
        if parent_name in self.child_concepts:
            return

        if parent_name not in self.parent_concepts:
            self.parent_concepts.setdefault(parent_name, gen)
        elif parent_name in self.parent_concepts and update:
            self.parent_concepts[parent_name] = gen

    def add_child(self, child_name, gen=1, update = True):
        # a node cannot be a child of itself
        if child_name == self.name:
            return

        if child_name in self.parent_concepts:
            return

        if child_name not in self.child_concepts:
            self.child_concepts.setdefault(child_name, gen)
        elif child_name in self.child_concepts and update:
            self.child_concepts[child_name] = gen

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


class ConceptConnector():
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
                       child_concepts={}, parent_concepts={}, synonims=[], antonims=[]):

        self.logger.info("processing concept " + new_concept_name)

        # handle new concept
        if new_concept_name not in self.concepts:
            self.logger.info("creating concept node for: " + new_concept_name)
            concept = ConceptNode(new_concept_name, data, parent_concepts, child_concepts, synonims, antonims)
            self.add_concept(new_concept_name, concept)

        # handle parent concepts
        for concept_name in parent_concepts:
            self.logger.info("checking if parent node exists: " + concept_name)

            # create parent if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name + " with child: " + new_concept_name)
                gen = parent_concepts[concept_name]
                concept = ConceptNode(concept_name, child_concepts={new_concept_name: gen})
                self.add_concept(concept_name, concept)


        # handle child concepts
        for concept_name in child_concepts:
            self.logger.info("checking if child node exists: " + concept_name)
            # create child if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name + " with parent: " + new_concept_name)
                gen = child_concepts[concept_name]
                concept = ConceptNode(concept_name, child_concepts={new_concept_name: gen})
                self.add_concept(concept_name, concept)


class ConceptCrawler():
    def _init__(self, center_node, target_node, concept_connector):
        # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/9
        # concept database
        self.concept_db = concept_connector
        # make tree of concepts
        self.tree = self.build_tree(concept_connector, target_node)
        # crawl path
        self.crawl_path = [center_node]
        # crawled antonims
        self.do_not_crawl = []
        # nodes we left behind without checking
        self.uncrawled = []
        # nodes we already checked
        self.crawled = []
        # crawl target
        self.target = target_node

    def build_tree(self, center_node, target_node, depth=20):
        tree = None
        return tree

    def find_path(self, center_node, target_node, path=[]):
        # find first path to connection
        path = path + [center_node]
        if center_node == target_node:
            return path

        if center_node not in self.tree:
            return None

        for node in self.tree[center_node]:
            if node not in path:
                newpath = self.find_path(center_node, target_node, path)
                if newpath:
                    return newpath
        return None

    def find_all_paths(self, center_node, target_node, path=[]):
        path = path + [center_node]

        if center_node == target_node:
            return [path]

        if center_node not in self.tree:
            return []

        paths = []
        for node in self.tree[center_node]:
            if node not in path:
                newpaths = self.find_all_paths(node, target_node, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

    def find_shortest_path(self, center_node, target_node, path=[]):

        path = path + [center_node]
        if center_node == target_node:
            return path

        if center_node not in self.tree:
            return None

        shortest = None

        for node in self.tree[center_node]:
            if node not in path:
                newpath = self.find_shortest_path(node, target_node, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

    def find_minimum_node_distance(self, center_node, target_node):
        return len(self.find_shortest_path(center_node, target_node))

    def get_total_crawl_distance(self):
        return len(self.crawled)

    def get_crawl_path_distance(self):
        return len(self.crawl_path
                   )

    def drunk_crawl(self, target):
        ''' Drunk_Crawl idea (because just stumbles around looking for familiar things until target is reached)

        crawl up - this will answer questions of the sort " is CenterNode a TargetNode ?"

        - start at CenterNode and build a concept_tree with all parent (and parents of parents...) nodes and N layers/hops (depth configurable)
        - while not in TargetNode
            - check if CurrentNode has synonims, if yes prefer synonim and smaller gen parents of synonim as next node
            - check if CurrentNode is antonym of any previous node, if yes go back and choose another
            - choose a random node coming out from CurrentNode, prefer higher gens
            - if no next node go back and search next guess
            - if end of tree return False
        - return True
        '''
        pass