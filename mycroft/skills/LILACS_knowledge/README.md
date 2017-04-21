# LILACS knowledge

loads all knowledge services, the services folder is monitored and all services loaded

this means more services can be added anytime

backends are read from config file, having a type corresponding to a service and any name

so you could choose "kitchen" backend if you felt like it

# config file example

          "knowledge": {
    "backends": {
      "wikipedia": {
        "type": "wikipedia",
        "active": true
      },
      "wikidata": {
        "type": "wikidata",
        "active": true
      },
      "wikihow": {
        "type": "wikihow",
        "active": true
      },
      "dbpedia": {
        "type": "dbpedia",
        "active": true
      },
      "concept net": {
        "type": "concept net",
        "active": true
      },
      "wordnik": {
        "type": "wordnik",
        "active": true
      },
      "wolfram alpha": {
        "type": "wolfram alpha",
        "active": true
      },
      "user": {
        "type": "user",
        "active": true
      }
    },
    "default-backend": "wolfram alpha"
    },


# usage

        from mycroft.skills.LILACS_knowledge.knowledgeservice import KnowledgeService

        service = KnowledgeService()
        data = service.adquire("info to adquire", "backend to use")

data param is different depending on backend

# TODO -> readme for each backend