# initial idea to populate nodes

import wptools



# wiki data
# broken?
musk = wptools.page('Stephen Fry').get_wikidata()

print "description: " + musk.description
print "what: " + musk.what
print "data:"
data = musk.wikidata
for key in data:
    print key + " : " + str(data[key])
print "\nproperties:"
props = musk.props
for prop in props:
    print prop + " : " + str(props[prop])

subject = "Elon Musk"
page = wptools.page(subject).get_query()
node_data = {}
node_data["pic"] = page.image('page')['url']
node_data["name"] = page.label
node_data["description"] = page.description
node_data["summary"] = page.extext
node_data["url"] = page.url

for data in node_data:
    print "\n" + data + " : " + str(node_data[data].encode('utf-8'))


print "\n infobox:"
page = wptools.page(subject).get_parse()
# TODO decent parsing, info is messy
for entry in page.infobox:
    print "\n" + entry + " : " + str(page.infobox[entry])
