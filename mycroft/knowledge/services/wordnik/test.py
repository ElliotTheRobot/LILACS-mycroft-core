from wordnik import *

apiUrl = 'http://api.wordnik.com/v4'
# get yoyr key here ->
apiKey = "39f2ba7ddaef2fe609301073d1e014ba34ecfb7574a20e83c"

client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)

def get_definitions(subject):
    definitions = wordApi.getDefinitions(subject,
                                         partOfSpeech='noun',
                                         sourceDictionaries='all',
                                         limit=5)
    defs = []
    try:
        for defi in definitions:
            defs.append(defi.text)
    except:
        pass
    return defs

def get_related_words(subject):
    res = wordApi.getRelatedWords(subject)
    words = {}
    try:
        for r in res:
            words.setdefault(r.relationshipType, r.words)
    except:
        pass
    return words


subject = "evil"
rels = get_related_words(subject)
defs = get_definitions(subject)

print "subject: " + subject

print "\ndefinitions:"
for defi in defs:
    print defi

print "\nrelationships:"
for rel in rels:
    print rel + " : " + str(rels[rel])
