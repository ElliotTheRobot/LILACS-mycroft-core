import math
import random

from mycroft.skills.LILACS_core.concept import ConceptConnector
from mycroft.skills.LILACS_core.crawl_log import getLogger as CrawlLogger
from mycroft.util.log import getLogger

__authors__ = ["jarbas", "heinzschmidt"]


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


class ConceptCrawler():
    def __init__(self, depth=20, concept_connector=None):
        # https://github.com/ElliotTheRobot/LILACS-mycroft-core/issues/9
        self.logger = CrawlLogger("Crawler", "Drunk")
        # concept database
        self.concept_db = concept_connector
        if self.concept_db is None:
            self.logger.error("no concept connector")
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

    def update_connector(self, connector):
        self.logger.info("Updating crawler connector")
        self.concept_db = connector

    def find_all_paths(self, center_node, target_node, path=[], direction="parents"):
        # TODO give a depth parameter, there may be "infinite" nodes and make this super slow
        path = path + [center_node]
        self.logger.info("Current Node: " + center_node)
        self.visits[center_node] += 1
        if center_node == target_node:
            self.logger.info("path found from " + path[0] + " to " + target_node)
            self.logger.info(path)
            return [path]

        if center_node not in self.concept_db.get_concept_names():
            # TODO load node and all connections from storage
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

        # TODO load node and all its connected nodes from storage
        # TODO if node not loaded ask knowledge service for node info
        # TODO send update nodes to storage

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
            self.logger.info("parents of " + node + " : " + str(nodes))
            # check if node as synonims
            synonims = []
            synonims = self.concept_db.get_synonims(node)
            self.logger.info("synonim of " + node + " : " + str(synonims))

            for synonim in synonims:
                # get connections of these synonims also
                self.logger.info("found synonim: " + synonim)
                self.crawled.append(synonim)
                self.logger.info("adding synonim connections to crawl list")
                p = {}
                try:
                    p = self.concept_db.get_parents(synonim)
                except:
                    pass
                self.logger.debug("synonim connections: " + str(p))
                for n in p:
                    nodes.setdefault(n, p[n])
        elif direction == "childs":
            nodes = self.concept_db.get_childs(node)
            # check if node as synonims
            synonims = self.concept_db.get_synonims(node)
            for synonim in synonims:
                # get connections of these synonims also
                self.logger.info("found synonim: " + synonim)
                self.logger.info("adding synonim connections to crawl list")
                c = {}
                try:
                    c = self.concept_db.get_childs(synonim)
                except:
                    pass
                self.logger.debug("synonim connections: " + str(c))
                for n in c:
                    nodes.setdefault(n, c[n])
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
        for node in self.concept_db.get_concept_names():
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
                # TODO check crawl_depth threshold
                #if crawl_depth >= self.depth:
                #    # do not crawl further
                #    self.logger.info("Maximum crawl depth reached: " + str(crawl_depth))
                #    return False
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
        # TODO load all relevant nodes into storage first
        # since nodes are "infinite" the easiest way to populate nodes is to do some crawls
        self.logger = CrawlLogger("Crawler", "Explorer")
        self.uncrawled = []  # none
        self.do_not_crawl = []  # none
        self.reset_visit_counter()
        self.crawled = self.concept_db.get_concept_names()
        self.crawl_path = self.find_shortest_path(center_node, target_node, direction=direction)
