import spotlight
host = "http://spotlight.sztaki.hu:2222/rest/annotate"
text = "the dog eats meat that comes from a cow and is an animal"
annotations = spotlight.annotate(host, text)

print "sentence: " + text

for annotation in annotations:
    #how sure we are this is about this dbpedia entry
    score = annotation["similarityScore"]
    print "\nscore : " + str(score)
    # entry we are talking about
    subject = annotation["surfaceForm"]
    print "subject: " + subject
    # smaller is closer to be main topic of sentence
    offset = annotation["offset"]
    print "offset: " + str(offset)
    # categorie of this <- linked nodes <- parsing for dbpedia search
    types = annotation["types"].split(",")
    for type in types:
        print "type: " + type
    #dbpedia link
    url = annotation["URI"]
    print "link: " + url

