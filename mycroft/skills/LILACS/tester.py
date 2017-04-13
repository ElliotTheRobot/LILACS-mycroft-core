import storage
from os.path import dirname

storagepath = str(".db/")

storage_inst = storage.ConceptStorage(storagepath)

print("Storage class created")

nodesdb = storage_inst.get_nodes_names()


def add_concept(concept_name, concept, concepts):
    if concept_name in concepts:
        #  merge fields
        for parent in concept.parent_concepts:
            if parent not in get_parents(concept_name):
                concepts[concept_name].add_parent(parent, gen=concept.parent_concepts[parent])
        for child in concept.child_concepts:
            if child not in get_childs(concept_name):
                concepts[concept_name].add_child(child, gen=concept.child_concepts[child])
        for antonim in concept.antonims:
            if antonim not in concepts[concept_name].antonims:
                concepts[concept_name].antonims.add_antonim(antonim)
        for synonim in concept.synonims:
            if synonim not in concepts[concept_name].synonims:
                concepts[concept_name].synonims.add_synonim(synonim)
    else:
        concepts.setdefault(concept_name, concept)

def get_childs(self, concept_name):
    return self.concepts[concept_name].child_concepts

def get_parents(self, concept_name):
    return self.concepts[concept_name].parent_concepts

def get_antonims(self, concept_name):
    return self.concepts[concept_name].antonims

def get_synonims(self, concept_name):
    return self.concepts[concept_name].synonims


add_concept("Santa", )

"""
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
"""
