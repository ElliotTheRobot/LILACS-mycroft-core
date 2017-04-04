from mycroft.skills.LILACS import ConceptCreator
from mycroft.skills.LILACS import ConceptStorage


def main():
    knowledge = ConceptCreator()
    storage = ConceptStorage()

    # create concepts for testing

    name = "human"
    child_concepts = ["male", "female"]
    parent_concepts = ["animal"]
    knowledge.create_concept(name, parent_concepts=parent_concepts,
        child_concepts=child_concepts)

    name = "joana"
    child_concepts = ["wife"]
    parent_concepts = ["human"]
    knowledge.create_concept(name, parent_concepts=parent_concepts,
        child_concepts=child_concepts)

    name = "animal"
    child_concepts = ["dog", "cow", "frog", "cat", "spider", "insect"]
    parent_concepts = ["alive"]
    knowledge.create_concept(name, parent_concepts=parent_concepts,
        child_concepts=child_concepts)

    # lets see what concept connector can deduce from here
    key = "joana"
    childs = knowledge.concepts[key].child_concepts
    parents = knowledge.concepts[key].parent_concepts

    print key + " can be: "
    for child in childs:
        print child

    print "\n"

    # in case of Joana everything here except human was deduced
    print key + " is:"
    for parent in parents:
        print parent

    # example of storage class usage
    storage.getNodeDataDictionary()
    storage.getNodeParent('cow', 0)
    storage.getNodeParent('cow', 1)

if __name__ == '__main__':
    main()
