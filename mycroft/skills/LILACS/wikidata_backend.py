# initial idea to populate nodes

import wptools

### wikipedia

musk = wptools.page('Elon Musk').get_query()
pic = musk.image('page')['url']

print musk.label
print pic
print musk.description
print musk.extext
print musk.url


musk = wptools.page('Elon Musk').get_parse()

for entry in musk.infobox:
    print entry + " : " + musk.infobox[entry]

# wiki data
# broken?
#musk = wptools.page('Elon Musk').get_wikidata()

#print musk.description
#print musk.what
#print musk.wikidata
