import json

__authors__ = ["jarbas", "heinzschmidt"]

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
        if (self._dataStorageType == "sqllite3"):
            """try:
                self._dataConnection = sqllite3.connect(self._dataStorageDB)
                self._dataConnStatus = 1
            except Exception as sqlerr:
                # log something
                print(("Database connection failed" + str(sqlerr)))
                self._dataConnStatus = 0
            """
        elif (self._dataStorageType == "json"):
            with open(self._storagepath + self._dataStorageDB) \
                    as datastore:
                self._dataJSON = json.load(datastore)

            if (self._dataJSON):
                self._dataConnStatus = 1
            else:
                self._dataConnStatus = 0

    def getNodesAll(self):
        returnVal = {}
        if (self._dataConnStatus == 1):
            # for p in self._dataJSON[]:
            returnVal = self._dataJSON
            return returnVal

    def getNodeDataDictionary(self, conceptname="cow"):
        returnVal = {}
        if (self._dataConnStatus == 1):
            for p in self._dataJSON[conceptname]:
                returnVal["data_dict"] = str(p["data_dict"])
        return returnVal

    def getNodeParent(self, conceptname="cow", generation=None):
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

    def getNodeChildren(self, conceptname="cow", generation=None):
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

    def getNodeSynonymn(self, conceptname="cow", generation=None):
        returnVal = {}
        if (self._dataConnStatus == 1):
            for node in self._dataJSON[conceptname]:
                if (generation is None):
                    for synonymn in node["synonymns"]:
                        returnVal = synonymn
                elif (generation <= len(node["synonymns"])):
                    for synonymn in node["synonymns"]:
                        if synonymn[str(generation)]:
                            returnVal = synonymn[str(generation)]
            return returnVal

    def getNodeAntonymn(self, conceptname="cow", generation=None):
        returnVal = {}
        if (self._dataConnStatus == 1):
            for node in self._dataJSON[conceptname]:
                if (generation is None):
                    for synonymn in node["antonymns"]:
                        returnVal = synonymn
                elif (generation <= len(node["antonymns"])):
                    for synonymn in node["antonymns"]:
                        if synonymn[str(generation)]:
                            returnVal = synonymn[str(generation)]
            return returnVal

    def getNodeLastUpdate(self, conceptname="cow"):
        returnVal = {}
        if (self._dataConnStatus == 1):
            for p in self._dataJSON[conceptname]:
                returnVal["last_update"] = str(p["last_update"])
        return returnVal
