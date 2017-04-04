import simplejson as json
from os.path import dirname


class ConceptStorage():

    _dataStorageType = ""
    _dataStorageUser = ""
    _dataStoragePass = ""
    _dataStorageDB = ""
    _dataConnection = None
    _dataConnStatus = 0
    _dataJSON = None

    def __init__(self, storagetype="json", database="lilacstorage.db"):
        self._dataStorageType = storagetype
        #self._dataStorageUser = username
        #self._dataStoragePass = password
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
        else:
            with open(dirname(__file__) + "/.db/" + self._dataStorageDB)\
             as datastore:
                self._dataJSON = json.load(datastore)

            if(self._dataJSON):
                self._dataConnStatus = 1
            else:
                self._dataConnStatus = 0

    def getNodeDataDictionary(self, conceptname="cow", conceptid=0):
        print("\n")
        if(self._dataConnStatus == 1):
            for p in self._dataJSON[conceptname]:
                print(('Concept: ' + conceptname))
                print(('Dictionary: ' + p["data_dict"]))

    def getNodeParent(self, conceptname="cow", generation=0):
        print("\r")
        if(self._dataConnStatus == 1):
            for p in self._dataJSON[conceptname]:
                print(('Concept: ' + conceptname))
                print(('Parent (' + str(generation + 1) + ') : ' +
                    str(p["parents"][0][str(generation)])))

    def getNodeChildren(self, conceptname="cow", generation=0):
        print("\r")
        if(self._dataConnStatus == 1):
            for p in self._dataJSON[conceptname]:
                print(('Concept: ' + conceptname))
                print(('Parent (' + str(generation + 1) + ') : ' +
                    str(p["parents"][0][str(generation)])))
