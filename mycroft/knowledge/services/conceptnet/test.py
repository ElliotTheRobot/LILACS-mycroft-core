import requests
subject = "satan"

parents = []
capable = []
has = []
desires = []
used = []
related = []
examples = []
location = []
other = []

obj = requests.get('http://api.conceptnet.io/c/en/'+subject).json()
for edge in obj["edges"]:
    rel = edge["rel"]["label"]
    node = edge["end"]["label"].lower().replace("a ", "").replace("an ", "").replace("the ", "")
    start = edge["start"]["label"].lower().replace("a ", "").replace("an ", "").replace("the ", "")
    if node in subject:
        continue
    if start != node and start not in other and start not in subject:
        other.append(start)
    if rel == "IsA":
        if node not in parents:
            parents.append(node)
    elif rel == "CapableOf":
        if node not in capable:
            capable.append(node)
    elif rel == "HasA":
        if node not in has:
            has.append(node)
    elif rel == "Desires":
        if node not in desires:
            desires.append(node)
    elif rel == "UsedFor":
        if node not in used:
            used.append(node)
    elif rel == "RelatedTo":
        if node not in related:
            related.append(node)
    elif rel == "AtLocation":
        if node not in location:
            location.append(node)
    usage = edge["surfaceText"]
    if usage is not None:
        examples.append(usage)


print "node: " + subject
print "is a: " + str(parents)#
print "has a: " + str(has)
print "used for: " + str(used)
print "related to: " + str(related)
print "desires: " + str(desires)
print "capable of: " + str(capable)
print "found at: " + str(location)
print "example usage: " + str(examples)
print "related nodes: " + str(other)