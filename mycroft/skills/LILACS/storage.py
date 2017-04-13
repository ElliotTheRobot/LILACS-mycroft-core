import json
from pprint import pprint

class ConceptStorage():
    _dataStorageDB = ""
    _dataConnection = None
    _dataConnStatus = 0
    _dataJSON = {}
    _storagepath = ""

    def __init__(self, storagepath, database="lilacstorage.db"):
        self._storagepath = storagepath
        self._dataStorageDB = database
        self.datastore_connect()

    def datastore_connect(self):
            #with open(self._storagepath + self._dataStorageDB) \
            #        as datastore:
            with open(self._storagepath + self._dataStorageDB, 'r') as myfile:
                file_content = myfile.read().replace("{}", "")
                self._dataJSON = json.loads(file_content)

            if (self._dataJSON):
                self._dataConnStatus = 1
            else:
                self._dataConnStatus = 0

    def get_nodes_names(self):
        returnVal = {}
        if (self._dataConnStatus == 1):
            returnVal = self._dataJSON
        return returnVal

    def get_nodes_list(self):
        returnVal = {}
        if (self._dataConnStatus == 1):
            nodenames = self._dataJSON
            returnVal = nodenames
        return returnVal

    def get_node_parents(self, conceptname="human", generation=None):
        returnVal = {}
        if (self._dataConnStatus == 1):
            for node in self._dataJSON[conceptname]:
                if (generation is None):
                    for parent in node["parents"]:
                        returnVal = parent
                elif (generation <= len(node["parents"])):
                    for parent in node["parents"]:
                        if parent[str(generation)]:
                            returnVal = parent[str(generation)]
        return returnVal

    def get_node_children(self, conceptname="human", generation=None):
        returnVal = {}
        if (self._dataConnStatus == 1):
            for node in self._dataJSON[conceptname]:
                if (generation is None):
                    for child in node["children"]:
                        returnVal = child
                elif (generation <= len(node["children"])):
                    for child in node["children"]:
                        if child[str(generation)]:
                            returnVal = child[str(generation)]
        return returnVal

    def get_node_attributes(self, conceptname="human"):
        returnVal = {}
        if (self._dataConnStatus == 1):
            for node in self._dataJSON[conceptname]:
                if(len(node["attrib"]) > 0):
                    for attribnodes in node["attrib"]:
                        returnVal = attribnodes;


