# LILACS storage

loads all storage services, the services folder is monitored and all services loaded

this means more services can be added anytime

backends are read from config file, having a type corresponding to a service and any name

so you could choose "cloud" backend if you felt like it

# config file example

          "storage": {
            "backends": {
              "local": {
                "type": "json",
                "active": true
              },
              "json": {
                "type": "json",
                "active": true
              }
            },
            "default-backend": "local"
            },


# usage

        from mycroft.skills.LILACS_storage.storageservice import StorageService

        service = StorageService()
        node = service.load("node name", "backend to use")
        service.save("node name", "backend", data={})

# TODO -> readme for each backend