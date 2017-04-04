from mycroft.skills.LILACS import ConceptConnector

def main():
    knowledge = ConceptConnector()

    # create concepts for testing
    # this will eventually interact with ConceptData and read / writeback to file for persistence

    name = "human"
    child_concepts = ["male", "female"]
    parent_concepts = ["animal"]
    knowledge.create_concept(name, parent_concepts=parent_concepts, child_concepts=child_concepts)

    name = "joana"
    child_concepts = ["wife"]
    parent_concepts = ["human"]
    knowledge.create_concept(name, parent_concepts=parent_concepts, child_concepts=child_concepts)

    name = "animal"
    child_concepts = ["dog", "cow", "frog", "cat", "spider", "insect"]
    parent_concepts = ["alive"]
    knowledge.create_concept(name, parent_concepts=parent_concepts, child_concepts=child_concepts)


    # lets see what concept connector can deduce from here
    key = "human"
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
