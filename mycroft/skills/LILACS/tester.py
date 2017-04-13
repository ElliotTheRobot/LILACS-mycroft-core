import storage
from os.path import dirname

storagepath = str(".db/")

storage_inst = storage.ConceptStorage(storagepath)

print("Storage class created")

nodesdb = storage_inst.get_nodes_names()

for nodes in nodesdb:
    name = nodes
    for node_details in nodesdb[name]:
        for node_parents in node_details["parents"]:
            parent_concepts = node_parents
        for node_childs in node_details["children"]:
            child_concepts = node_childs
        for node_attribs in node_details["attrib"]:
            for node_synonyms in node_attribs["synonymns"]:
                synonims = node_synonyms
            for node_antonyms in node_attribs["antonyms"]:
                antonimns = node_antonyms
