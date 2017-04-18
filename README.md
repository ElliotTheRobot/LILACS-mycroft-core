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
- Wordnik
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




### Current Output from each knowledge backend

still working on parsing all this, but currently we can fetch the following info


Wolfram Alpha

        question: frog
        answer: frogs, toads... (animals) is Anura
        parents: {u'toads': [u'species', u'eukaryote', u'animal', u'amphibian'], u'animals': [u'species', u'eukaryote', u'animal']}
        relevant_nodes: [u'frogs', u'anura', u'toads', u'animals']
        synonims: {u'anura': u'frog'}


        question: do aliens exist?
        answer: Drake equation : number of communicating civilizations in the Milky Way, 10
        parents: {}
        relevant_nodes: [u'milky', u'communicating', u'civilizations', u'drake equation', u'number']
        synonims: {u'aliens': u'extraterrestrial life', u'exist': u'existence', u'communicating': u'communication'}

Wikipedia


        name : Elon Musk

        description : entrepreneur and inventor from South Africa

        url : https://en.wikipedia.org/wiki/Elon_Musk

        pic : https://upload.wikimedia.org/wikipedia/commons/4/49/Elon_Musk_2015.jpg

        summary : Elon Reeve Musk (/ˈiːlɒn ˈmʌsk/; born June 28, 1971) is a South African-born Canadian-American business magnate, investor, engineer, and inventor.

        He is the founder, CEO, and CTO of SpaceX; co-founder, CEO, and product
        architect of Tesla Inc.; co-founder and chairman of SolarCity; co-chairman of
        OpenAI; co-founder of Zip2; and founder of X.com, which merged with Confinity
        and took the name PayPal. As of March 2017, he has an estimated net worth of
        $13.9 billion, making him the 80th wealthiest person in the world. In December
        2016, Musk was ranked 21st on Forbes list of The World's Most Powerful People.......


        known_for : [[SpaceX]], [[PayPal]], [[Tesla Inc.]], [[Hyperloop]], [[SolarCity]], [[OpenAI]], [[The Boring Company]], [[Neuralink]], [[Zip2]]

        citizenship : {{Plainlist|
        *South African (1971–present)
        *Canadian (1971–present)
        *American (2002–present)
        }}

        image : Elon Musk 2015.jpg

        birth_place : [[Pretoria]], [[Transvaal Province|Transvaal]], [[South Africa]]

        networth : [[US$]]14 Billion (March 31, 2017)

        spouse : {{Plainlist|

            |Marriage|[[Justine Musk]]|2000|2008|reason|=|divorced|
            [[Talulah Riley]] (|abbr|m.|married| 2010–|abbr|div.|divorced| 2012; |abbr|m.|married| 2013–|abbr|div.|divorced| 2016)|ref|{{Cite news|url=https://www.theguardian.com/technology/2016/mar/21/elon-musk-talulah-riley-file-divorce-second-marriage|title=Actor Talulah Riley files to divorce billionaire Elon Musk, again|date=March 21, 2016|accessdate=April 20, 2016|work=[[The Guardian]]|quote="The pair first married in 2010 and divorced in 2012. They remarried 18 months later."}}||ref| name="withdrawn"|{{cite web|url=http://www.dailymail.co.uk/news/article-3185591/Elon-Musk-withdraws-divorce-papers-against-wife-Talulah-Riley-one-month-pair-spotted-holding-hands-Allen-Company-conference.html|title=Elon Musk withdraws Talulah Riley divorce papers after being spotted at Allen & Company conference|date=August 5, 2015|work=Mail Online}}||
            }}

        children : 6 sons

        occupation : Entrepreneur, engineer, inventor, investor

       .... infobox not fully shown here

Wikidata

        subject: Stephen Fry

        description: English comedian, actor, writer, presenter, and activist

        what: human

        data:
        website : http://www.stephenfry.com
        category : Category:Stephen Fry
        citizenship : United Kingdom
        image : Stephen Fry cropped.jpg
        instance : human
        IMDB : nm0000410
        birth : +1957-08-24T00:00:00Z
        movement : atheism

        properties:
        P135 : [u'Q7066']
        P345 : [u'nm0000410']
        P910 : [u'Q8817795']
        P27 : [u'Q145']
        P856 : [u'http://www.stephenfry.com']
        P569 : [u'+1957-08-24T00:00:00Z']
        P18 : [u'Stephen Fry cropped.jpg']
        P31 : [u'Q5']



Dbpedia

        subject: living beings
        link: http://dbpedia.org/resource/Life
        picture : ['http://commons.wikimedia.org/wiki/Special:FilePath/Ruwenpflanzen.jpg']
        abstract : Life is a characteristic distinguishing physical entities having biological processes (such as signaling and self-sustaining processes) from those that do not, either because such functions have ceased (death), or because they lack such functions and are classified as inanimate. Various forms of life exist such as plants, animals, fungi, protists, archaea, and bacteria. The criteria can at times be ambiguous and may or may not define viruses, viroids or potential artificial life as living. Biology is the primary science concerned with the study of life, although many other sciences are involved. Throughout history there have been many theories about life including materialism, hylomorphism and vitalism. Even today it is a challenge for scientists and philosophers to define life. The smallest contiguous unit of life is called an organism. Organisms are composed of one or more cells, undergo metabolism, maintain homeostasis, can grow, respond to stimuli, reproduce (either sexually or asexually) and, through evolution, adapt to their environment in successive generations. A diverse array of living organisms can be found in the biosphere of Earth, and the properties common to these organisms are a carbon- and water-based cellular form with complex organization and heritable genetic information. Abiogenesis is the natural process of life arising from non-living matter, such as simple organic compounds. The earliest life on Earth arose at least 3.5 billion years ago, during the Eoarchean Era when sufficient crust had solidified following the molten Hadean Eon. The earliest physical evidence of life on Earth is biogenic graphite from 3.7 billion-year-old metasedimentary rocks found in Western Greenland and microbial mat fossils in 3.48 billion-year-old sandstone found in Western Australia. Some theories, such as the Late Heavy Bombardment theory, suggest that life on Earth may have started even earlier, as early as 4.1-4.4 billion years ago. According to one of the researchers, "If life arose relatively quickly on Earth ... then it could be common in the universe." The mechanism by which life began on Earth is unknown, although many hypotheses have been formulated. Since emerging, life has evolved into a variety of forms, which have been classified into a hierarchy of taxa. Life can survive and thrive in a wide range of conditions. Nonetheless, it is estimated that 99 percent of all species, amounting to over five billion species, that ever lived on Earth are extinct. Estimates on the number of Earth's current species range from 10 million to 14 million, of which about 1.2 million have been documented and over 86 percent have not yet been described. The chemistry leading to life may have begun shortly after the Big Bang, 13.8 billion years ago, during a habitable epoch when the Universe was only 10–17 million years old. Though life is confirmed only on the Earth, many think that extraterrestrial life is not only plausible, but probable or inevitable. Other planets and moons in the Solar System and other planetary systems are being examined for evidence of having once supported simple life, and projects such as SETI are trying to detect radio transmissions from possible alien civilizations.
        external_links : ['http://astro-ecology.com/', 'http://rationalphilosophy.net/index.php/the-book', 'http://www.edge.org/3rd_culture/kauffman03/kauffman_index.html', 'http://www.astro-ecology.com/PDFSeedingtheUniverse2005Book.pdf', 'http://plato.stanford.edu/entries/life/', 'http://logic-law.com/index.php?title=The_Kingdoms_of_Life']
        related_subjects : ['Life', 'Entropy', 'Biology', 'Nature', 'Life']



WikiHow


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


ConceptNet


            node: chicken
            is a: [u'food', u'meat']
            has a: []
            used for: []
            related to: [u'bird', u'hen', u'rooster', u'animal', u'farm', u'poultry', u'eggs', u'food', u'fowl', u'egg', u'meat', u'fried', u'wings']
            desires: []
            capable of: [u'cross road', u'lay eggs', u'produce eggs']
            found at: []
            example usage: [u'[[chicken]] is related to [[bird]]', u'[[chicken]] is related to [[hen]]', u'[[the chicken]] can [[cross the road]]', u'[[chicken]] is related to [[rooster]]', u'[[chicken]] is related to [[animal]]', u'[[chicken]] is a type of [[food]]', u'[[chicken]] is related to [[farm]]', u'[[chicken]] is related to [[poultry]]', u'[[chicken]] is related to [[eggs]]', u'[[chicken]] is related to [[food]]', u'[[chicken]] is a type of [[meat]]', u'[[chicken]] is related to [[fowl]]', u'[[chicken]] is related to [[egg]]', u'[[chicken]] is related to [[meat]]', u'[[chicken]] is related to [[fried]]', u'[[a chicken]] can [[lay eggs]]', u'[[A chicken]] can [[produce eggs]]', u'[[chicken]] is related to [[wings]]']
            related nodes: []


WordNik

        definitions:
        A member of the genus Homo and especially of the species H. sapiens.
        A person:  the extraordinary humans who explored Antarctica.
        A human being, whether man, woman or child.
        A human being.
        A human being; a member of the family of mankind.

        relationships:
        synonym : [u'hominal', u'hominine', u'humanistic', u'earthborn', u'mortal', u'humane', u'earthling', u'clod', u'Christian', u'man']
        unknown : [u'Religion & Spirituality', u'Health & Medicine', u'History', u'Science', u'LGBTQ']
        equivalent : [u'fallible', u'hominine', u'hominal', u'hominid', u'anthropomorphous', u'earthborn', u'imperfect', u'humanlike', u'anthropomorphic', u'weak']
        cross-reference : [u'human sign']
        rhyme : [u'Neumann', u'Newman', u'Schuman', u'Schumann', u'Truman', u'acumen', u'albumin', u'bitumen', u'crewman', u'cumin']
        etymologically-related-term : [u'humanity', u'humanitarian', u'humane', u'humanitarianism']
        same-context : [u'own', u'natural', u'individual', u'young', u'national', u'religious', u'pleonastic', u'ill', u'active', u'every']
        antonym : [u'divine', u'devilish', u'superhuman', u'deity', u'animal']



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
