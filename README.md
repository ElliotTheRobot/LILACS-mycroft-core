MyCroft - LILACS Fork 
=====================
See Core issue : https://github.com/MycroftAI/mycroft-core/issues/629

## LILACS ( Lilacs Is a Learning And Comprehension Subsystem )

### Purpose

Deducing answers and gathering knowledge for offline usage. Lilacs will be called when no intent is matched 

![alt tag](https://github.com/ElliotTheRobot/LILACS-mycroft-core/blob/dev/lilacs-core.jpg)


This fork will be merged / released as add-on when it is complete

The idea is that mycroft gathers knowledge about anything it hears, searches info on several possible backends when asked, and learns from user input

This knowledge comes both in the form of connections/properties of subjects and text info, this allows mycroft:

- to be vocally programmed about relationships of things (music tastes, family relationships)
- to gather all the info from the internet, more backends can be added any time
- to deduce answers from node relationships and answer several kinds of questions
- to be more personal
    - "individual" knowledge between units
    - a "personality" depending on usage history
    - can "talk/rant" about subjects
- store gathered knowledge in several fashions
    - collective database
    - personal database


### Where does the knowledge come from

- WolframAlpha
- ConceptNet
- Wikipedia
- Wikidata
- Dbpedia
- Wikihow
- Ask user

### Info-node structure

information and their relationship is stored in concept nodes, kinda like a single subjet at a time


    Node:
        name:
        type: "informational"   <- all discussed nodes so far are informational
        Connections:
            synonims: []  <- is the same as
            antonims: [] <- can never be related to
            parents: []  <- is an instance of
            childs: [] <- can have the following instances 
            cousins: [] <- somewhat related subjects 
            spawns: []  <- what comes from this?
            spawned_by: [] <- where does this come from?
            consumes: [] <- what does this need/spend ?
            consumed_by: []  <- what consumes this?
            parts : [ ] <- what smaller nodes can this be divided into?
            part_off: [ ] <- what can be made out of this?
        Data:
             description: wikidata description_field
             abstract: dbpedia abstract
             summary: wikipedia_summary
             pics: [ wikipedia pic, dbpedia pic ]
             infobox: {wikipedia infobox}
             wikidata: {wikidata_dict}
             props: [wikidata_properties] <- if we can parse this appropriatly we can make connections
             links: [ wikipedia link, dbpedia link  ]
             external_links[ suggested links from dbpedia]


### Questions LILACS can answer

a question parser is in place so mycroft knows whats being asked

      Question: how to kill animals ( a cow ) and make meat
      question_type: how
      center_node: kill
      target_node: animals
      parents: {u'animals': [u'Species', u'Eukaryote', u'Animal'], u'cow': [u'Species', u'Eukaryote', u'Animal', u'Mammal']}
      relevant_nodes: [u'meat', u'cow']
      synonims: {u'kill': u'murder', u'cow': u'cattle'}



There is a wolfram alpha knowledge backend, this should answer most questions

        question: how much wood can a woodchuck chuck
        answer:  A woodchuck would chuck all the wood he could chuck if a woodchuck could chuck wood.,
        According to the tongue twister, although the paper "The Ability of Woodchucks to Chuck Cellulose Fibers" by P.A. Paskevich and T.B. Shea in Annals of Improbable Research vol. 1, no. 4, pp. 4-9, July/August 1995, concluded that a woodchuck can chuck 361.9237001 cubic centimeters of wood per day.

        question: when will the world end
        answer: time until the end of the world is 5 billion years, (The world will effectively end 5 billion years from now when the Sun becomes a red giant. As a red giant, the Sun will lose roughly 30% of its mass and (without tidal effects) the Earth will move to an orbit 1.7 AU from the Sun when the star reaches its maximum radius. Therefore, the planet is expected to escape envelopment by the expanded Sun's sparse outer atmosphere, though most, if not all, remaining life will be destroyed because of the Sun's increased luminosity. However, a more recent simulation indicates that Earth's orbit will decay due to tidal effects and drag, causing it to enter the red giant Sun's atmosphere and be destroyed.)

        question: does god exist
        answer:  I'm sorry, but a poor computational knowledge engine, no matter how powerful, not capable of providing a simple answer to that question.

        question: what are humans
        answer: human (animal) is Homo sapiens


the core of LILACS is meant to be used when wolfram doesnt know, or there is no internet connection, much more to come


      - compare -> is "this" and example of "that"

> Speak: answer to is frog a cat is False

      - examples -> give examples of "this"

> Speak: joana is an example of human

> Speak: maria is an example of human


      - common -> "this" and "that" are both "something"

> Speak: frog are animal like human

> Speak: frog are living being like human

      - what -> "this" is "that", "that other thing" and "something"

> Speak: cow is animal

> Speak: cow is living being

      - why? -> "this" is A, A is B, B is C, C is "that", therefore "this" is "that"

> Speak: answer to is frog a living being is True

> Speak: frog is animal

> Speak: animal is living being


      - how? -> step 1, step 2, step 3
      
This is currently difficult to answer using nodes, wikihow backend handles these

    How to Hardboil Eggs in a Microwave
    
    step 0 : Place your eggs in a microwave safe bowl.
    http://pad1.whstatic.com/images/thumb/b/b2/Hardboil-Eggs-in-a-Microwave-Step-1-Version-3.jpg/aid238320-v4-728px-Hardboil-Eggs-in-a-Microwave-Step-1-Version-3.jpg
    step 1 : Add water to the bowl.
    http://pad2.whstatic.com/images/thumb/a/a5/Hardboil-Eggs-in-a-Microwave-Step-2-Version-3.jpg/aid238320-v4-728px-Hardboil-Eggs-in-a-Microwave-Step-2-Version-3.jpg
    step 2 : Pour one tablespoon of salt into the bowl.
    http://pad1.whstatic.com/images/thumb/5/53/Hardboil-Eggs-in-a-Microwave-Step-3-Version-3.jpg/aid238320-v4-728px-Hardboil-Eggs-in-a-Microwave-Step-3-Version-3.jpg
    step 3 : Cook the eggs for up to 12 minutes.
    http://pad3.whstatic.com/images/thumb/9/9b/Hardboil-Eggs-in-a-Microwave-Step-4-Version-3.jpg/aid238320-v4-728px-Hardboil-Eggs-in-a-Microwave-Step-4-Version-3.jpg
    step 4 : Let the eggs cool down before you touch them.
    http://pad2.whstatic.com/images/thumb/1/10/Hardboil-Eggs-in-a-Microwave-Step-5-Version-3.jpg/aid238320-v4-728px-Hardboil-Eggs-in-a-Microwave-Step-5-Version-3.jpg
    step 5 : Enjoy your hard-boiled eggs.
    http://pad1.whstatic.com/images/thumb/8/80/Hardboil-Eggs-in-a-Microwave-Step-6-Version-3.jpg/aid238320-v4-728px-Hardboil-Eggs-in-a-Microwave-Step-6-Version-3.jpg




Mycroft [![Build Status](https://travis-ci.org/MycroftAI/mycroft-core.svg?branch=master)](https://travis-ci.org/MycroftAI/mycroft-core)
==========

NOTE: The default branch for this repo is dev. This should be considered a working beta. If you want to clone a more stable version, switch over to the 'master' branch.  

Full docs at: https://docs.mycroft.ai

Release notes at: https://docs.mycroft.ai/release-notes

Pair Mycroft instance at: https://home.mycroft.ai

Join the Mycroft Slack(chat) channel: http://mycroft-ai-slack-invite.herokuapp.com/

Looking to join in developing?  Check out the [Project Wiki](../../wiki/Home) for tasks you can tackle!

# Getting Started

### Ubuntu/Debian, Arch, or Fedora
- Run the build host setup script for your OS (Ubuntu/Debian: `build_host_setup_debian.sh`, Arch: `build_host_setup_arch.sh`, Fedora: `build_host_setup_fedora.sh`). This installs necessary packages, please read it
- Run `dev_setup.sh` (feel free to read it, as well)
- Restart session (reboot computer, or logging out and back in might work).

### Other environments

The following packages are required for setting up the development environment,
 and are what is installed by `build_host_setup` scripts.

 - `git`
 - `python 2`
 - `python-setuptools`
 - `python-virtualenv`
 - `pygobject`
 - `virtualenvwrapper`
 - `libtool`
 - `libffi`
 - `openssl`
 - `autoconf`
 - `bison`
 - `swig`
 - `glib2.0`
 - `s3cmd`
 - `portaudio19`
 - `mpg123`
 - `flac`
 - `curl`

## Home Device and Account Manager
Mycroft AI, Inc. - the company behind Mycroft maintains the Home device and account management system. Developers can sign up at https://home.mycroft.ai

By default the Mycroft software is configured to use Home, upon any request such as "Hey Mycroft, what is the weather?", you will be informed that you need to pair and Mycroft will speak a 6-digit code, which you enter into the pairing page on the [Home site](https://home.mycroft.ai).

Once signed and a device is paired, the unit will use our API keys for services, such as the STT (Speech-to-Text) API. It also allows you to use our API keys for weather, Wolfram-Alpha, and various other skills.

Pairing information generated by registering with Home is stored in:

`~/.mycroft/identity/identity2.json` <b><-- DO NOT SHARE THIS WITH OTHERS!</b>

It's useful to know the location of the identity file when troubleshooting device pairing issues.

## Using Mycroft without Home.
If you do not wish to use our service, you may insert your own API keys into the configuration files listed below in <b>configuration</b>.

The place to insert the API key looks like the following:

`[WeatherSkill]`

`api_key = ""`

Put the relevant key in between the quotes and Mycroft Core should begin to use the key immediately.

### API Key services

- [STT API, Google STT](http://www.chromium.org/developers/how-tos/api-keys)
- [Weather Skill API, OpenWeatherMap](http://openweathermap.org/api)
- [Wolfram-Alpha Skill](http://products.wolframalpha.com/api/)

These are the keys currently in use in Mycroft Core.

## Configuration
Mycroft configuration consists of 3 possible config files.
- `mycroft-core/mycroft/configuration/mycroft.conf`
- `/etc/mycroft/mycroft.conf`
- `$HOME/.mycroft/mycroft.conf`

When the configuration loader starts, it looks in those locations in that order, and loads ALL configuration. Keys that exist in multiple config files will be overridden by the last file to contain that config value. This results in a minimal amount of config being written for a specific device/user, without modifying the distribution files.

# Running Mycroft Quick Start
To start the essential tasks run `./mycroft.sh start`. Which will start the service, skills, voice and cli (using --quiet mode) in a detched screen and log the output of the screens to the their respective log files (e.g. ./log/mycroft-service.log).
Optionally you can run `./mycroft.sh start -v` Which will start the service, skills and voice. Or `./mycroft.sh start -c` Which will start the service, skills and cli.

To stop Mycroft run `./mycroft.sh stop`. This will quit all of the detached screens.
To restart Mycroft run './mycroft.sh restart`.

Quick screen tips
- run `screen -list` to see all running screens
- run `screen -r [screen-name]` (e.g. `screen -r mycroft-service`) to reatach a screen
- to detach a running screen press `ctrl + a, ctrl + d`
See the screen man page for more details 

# Running Mycroft
## With `start.sh`
Mycroft provides `start.sh` to run a large number of common tasks. This script uses the virtualenv created by `dev_setup.sh`. The usage statement lists all run targets, but to run a Mycroft stack out of a git checkout, the following processes should be started:

- run `./start.sh service`
- run `./start.sh skills`
- run `./start.sh voice`

*Note: The above scripts are blocking, so each will need to be run in a separate terminal session.*

## Without `start.sh`

Activate your virtualenv.

With virtualenv-wrapper:
```
workon mycroft
```

Without virtualenv-wrapper:
```
source ~/.virtualenvs/mycroft/bin/activate
```


- run `PYTHONPATH=. python client/speech/main.py` # the main speech detection loop, which prints events to stdout and broadcasts them to a message bus
- run `PYTHONPATH=. python client/messagebus/service/main.py` # the main message bus, implemented via web sockets
- run `PYTHONPATH=. python client/skills/main.py` # main skills executable, loads all skills under skills dir

*Note: The above scripts are blocking, so each will need to be run in a separate terminal session. Each terminal session will require that the virtualenv be activated. There are very few reasons to use this method.*

# FAQ/Common Errors

#### When running mycroft, I get the error `mycroft.messagebus.client.ws - ERROR - Exception("Uncaught 'error' event.",)`

This means that you are not running the `./start.sh service` process. In order to fully run Mycroft, you must run `./start.sh service`, `./start.sh skills`, and `./start.sh voice`/`./start.sh cli` all at the same time. This can be done using different terminal windows, or by using the included `./mycroft.sh start`, which runs all four process using `screen`.
