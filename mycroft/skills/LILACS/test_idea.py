

class Concept():
    def __init__(self, name, data = {}, parent_concepts = [], child_concepts = [], synonims = [], antonims = []):
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

    def add_parent(self, parent_name):
        if parent_name not in self.parent_concepts:
            self.parent_concepts.append(parent_name)

    def add_child(self, child_name):
        if child_name not in self.child_concepts:
            self.child_concepts.append(child_name)

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
        i = 0
        for name in self.parent_concepts:
            if name == parent_name:
                self.parent_concepts.pop(i)
                return
            i +=1

    def remove_child(self, child_name):
        i = 0
        for name in self.child_concepts:
            if name == child_name:
                self.child_concepts.pop(i)
                return
            i += 1


class KnowledgeBase():
    def __init__(self, concepts = {}):
        self.concepts = concepts

    def add_concept(self, concept_name, concept):
        if concept_name in self.concepts:
            #  merge fields
            for parent in concept.parent_concepts:
                if parent not in self.concepts[concept_name].parent_concepts:
                    self.concepts[concept_name].parent_concepts.append(parent)
            for child in concept.child_concepts:
                if child not in self.concepts[concept_name].child_concepts:
                    self.concepts[concept_name].child_concepts.append(child)
            for antonim in concept.antonims:
                if antonim not in self.concepts[concept_name].antonims:
                    self.concepts[concept_name].antonims.append(antonim)
            for synonim in concept.synonims:
                if synonim not in self.concepts[concept_name].synonims:
                    self.concepts[concept_name].synonims.append(synonim)
            # TODO merge data

        else:
            self.concepts.setdefault(concept_name, concept)

    def remove_concept(self, concept_name ):
        self.concepts.pop(concept_name)

    def create_concept(self, new_concept_name, data = {}, child_concepts = [], parent_concepts = []):
        # handle parent concepts
        for concept_name in parent_concepts:
            # create parent if it doesnt exist
            if concept_name not in self.concepts:
                concept = Concept(concept_name, child_concepts=[new_concept_name])
                self.add_concept(concept_name, concept)
            else:
            # add child to parent if it exists
                self.concepts[concept_name].add_child(new_concept_name)

            #add parents of parents (if jon is human and humans are animals, jon is an animal)
            #for grandpa_concept_name in self.concepts[concept_name].parent_concepts:
            #    self.create_concept(grandpa_concept_name, child_concepts= [concept_name, new_concept_name])

        # handle child concepts
        for concept_name in child_concepts:
            # create child if it doesnt exist
            if concept_name not in self.concepts:
                concept = Concept(concept_name, parent_concepts=[new_concept_name])
                self.add_concept(concept_name, concept)
            else:
            # add parent to child if it exists
                self.concepts[concept_name].add_parent(new_concept_name)

        concept = Concept(new_concept_name, data, parent_concepts, child_concepts)
        self.add_concept(new_concept_name, concept)


knowledge = KnowledgeBase()



name = "human"
child_concepts = ["male", "female", "name"]
parent_concepts = ["Animal", "Mammal"]
knowledge.create_concept(name, parent_concepts=parent_concepts, child_concepts=child_concepts)

name = "Joana"
child_concepts = ["wife"]
parent_concepts = ["human", "name", "female"]
knowledge.create_concept(name, parent_concepts=parent_concepts, child_concepts=child_concepts)

name = "Animal"
child_concepts = ["dog", "cow", "frog", "cat", "spider", "insect"]
parent_concepts = ["alive"]
knowledge.create_concept(name, parent_concepts=parent_concepts, child_concepts=child_concepts)


key = "Animal"
childs = knowledge.concepts[key].child_concepts
parents = knowledge.concepts[key].parent_concepts

print key + " can be: "
for child in childs:
    print child

print "\n"

print key + " are:"

for parent in parents:
    print parent

