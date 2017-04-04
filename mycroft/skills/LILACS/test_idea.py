from mycroft.skills.LILACS import ConceptCreator
from mycroft.skills.LILACS import ConceptStorage


def main():
    knowledge = ConceptCreator()
    storage = ConceptStorage()

    print "\n reading concepts from db test\n"
    # example of storage class usage
    storage.getNodeDataDictionary()
    storage.getNodeParent('cow', 0)
    storage.getNodeParent('cow', 1)

    # create concepts for testing
    print "\ncreating coded concepts test\n"
    name = "human"
    child_concepts = {"male": 1, "female": 1}
    parent_concepts = {"animal": 1}
    knowledge.create_concept(name, parent_concepts=parent_concepts,
                             child_concepts=child_concepts)

    name = "joana"
    child_concepts = {"wife": 1}
    parent_concepts = {"human": 1, "female": 2}
    knowledge.create_concept(name, parent_concepts=parent_concepts,
                             child_concepts=child_concepts)

    name = "animal"
    child_concepts = {"dog": 1, "cow": 1, "frog": 1, "cat": 1, "spider": 1, "insect": 1}
    parent_concepts = {"alive": 1}
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

if __name__ == '__main__':
    main()
