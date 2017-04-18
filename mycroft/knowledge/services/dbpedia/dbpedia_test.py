import spotlight
import json
import urlfetch

host = "http://spotlight.sztaki.hu:2222/rest/annotate"


def scrap_resource_page(link):
    u = link.replace("http://dbpedia.org/resource/", "http://dbpedia.org/data/") + ".json"
    data = urlfetch.fetch(url=u)
    json_data = json.loads(data.content)
    dbpedia = {}
    dbpedia["related_subjects"] = []
    dbpedia["picture"] = []
    dbpedia["external_links"] = []
    dbpedia["abstract"] = ""
    for j in json_data[link]:
        if "#seeAlso" in j:
            # complimentary nodes
            for entry in json_data[link][j]:
                value = entry["value"].replace("http://dbpedia.org/resource/", "").replace("_", " ").encode("utf8")
                if value not in dbpedia["related_subjects"]:
                    dbpedia["related_subjects"].append(value)
        elif "wikiPageExternalLink" in j:
            # links about this subject
            for entry in json_data[link][j]:
                value = entry["value"].encode("utf8")
                dbpedia["external_links"].append(value)
        elif "subject" in j:
            # relevant nodes
            for entry in json_data[link][j]:
                value = entry["value"].replace("http://dbpedia.org/resource/Category:", "").replace("_", " ").encode("utf8")
                if value not in dbpedia["related_subjects"]:
                    dbpedia["related_subjects"].append(value)
        elif "abstract" in j:
            # english description
            dbpedia["abstract"] = \
                [abstract['value'] for abstract in json_data[link][j] if abstract['lang'] == 'en'][0].encode("utf8")
        elif "depiction" in j:
            # pictures
            for entry in json_data[link][j]:
                value = entry["value"].encode("utf8")
                dbpedia["picture"].append(value)
        elif "isPrimaryTopicOf" in j:
            # usually original wikipedia link
            for entry in json_data[link][j]:
                value = entry["value"].encode("utf8")
                #dbpedia["primary"].append(value)
        elif "wasDerivedFrom" in j:
            # usually wikipedia link at scrap date
            for entry in json_data[link][j]:
                value = entry["value"].encode("utf8")
                #dbpedia["derived_from"].append(value)
        elif "owl#sameAs" in j:
            # links to dbpedia in other languages
            for entry in json_data[link][j]:
                value = entry["value"].encode("utf8")
                if "resource" in value:
                    #dbpedia["same_as"].append(value)
                    pass

    return dbpedia

def tag(text):
    annotations = spotlight.annotate(host, text)
    for annotation in annotations:
        #how sure we are this is about this dbpedia entry
        score = annotation["similarityScore"]
       # print "\nscore : " + str(score)
        # entry we are talking about
        subject = annotation["surfaceForm"]
        print "subject: " + subject
        # smaller is closer to be main topic of sentence
        offset = annotation["offset"]
       # print "offset: " + str(offset)
        # categorie of this <- linked nodes <- parsing for dbpedia search
        types = annotation["types"].split(",")
        for type in types:
            if type != "":
                print "parent: " + type
        #dbpedia link
        url = annotation["URI"]
        print "link: " + url
        return url


text = "living beings"
print "sentence: " + text
link = tag(text)
dbpedia = scrap_resource_page(link)
for entry in dbpedia:
    print entry + " : " + str(dbpedia[entry])
