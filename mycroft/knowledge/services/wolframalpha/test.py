# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.


from StringIO import StringIO

import re
import wolframalpha
from requests import HTTPError

from mycroft.api import Api
from mycroft.util.log import getLogger
from mycroft.skills.question_parser import LILACSQuestionParser

__author__ = 'seanfitz'

LOG = getLogger(__name__)


class WAApi(Api):
    def __init__(self):
        super(WAApi, self).__init__("wa")

    def get_data(self, response):
        return response

    def query(self, input):
        data = self.request({"query": {"input": input}})
        return wolframalpha.Result(StringIO(data.content))


PIDS = ['Value', 'NotableFacts:PeopleData', 'BasicInformation:PeopleData',
        'Definition', 'DecimalApproximation']

key = "7WE57H-AEJTU5U3HV"
client = wolframalpha.Client(key)


def get_result(res):
    try:
        return next(res.results).text
    except:
        result = None
        try:
            for pid in PIDS:
                result = __find_pod_id(res.pods, pid)
                if result:
                    result = result[:5]
                    break
            if not result:
                result = __find_num(res.pods, '200')
            return result
        except:
            return result

def __find_pod_id(pods, pod_id):
    for pod in pods:
        if pod_id in pod.id:
            return pod.text
    return None

def __find_num(pods, pod_num):
    for pod in pods:
        if pod.node.attrib['position'] == pod_num:
            return pod.text
    return None

def _find_did_you_mean(res):
    value = []
    root = res.tree.find('didyoumeans')
    if root is not None:
        for result in root:
            value.append(result.text)
    return value

def process_wolfram_string(text, lang):
    # Remove extra whitespace
    text = re.sub(r" \s+", r" ", text)

    # Convert | symbols to commas
    text = re.sub(r" \| ", r", ", text)

    # Convert newlines to commas
    text = re.sub(r"\n", r", ", text)

    # Convert !s to factorial
    text = re.sub(r"!", r",factorial", text)

    regex = "(1,|1\.) (?P<Definition>.*) (2,|2\.) (.*)"
    list_regex = re.compile(regex)

    match = list_regex.match(text)
    if match:
        text = match.group('Definition')

    return text

def ask_wolfram(query, lang="en-us"):
    others = []
    result = None
    try:
        res = client.query(query)
        result = get_result(res)
        if result is None:
            others = _find_did_you_mean(res)
    except HTTPError as e:
        print "mycroft.not.paired"
    except:
        print "error"

    response = ["no answer"]
    if result:
        input_interpretation = __find_pod_id(res.pods, 'Input')
        verb = "is"

        if "|" in result:  # Assuming "|" indicates a list of items
            verb = ":"

        result = process_wolfram_string(result, lang)
        input_interpretation = \
            process_wolfram_string(input_interpretation, lang)
        response = "%s %s %s" % (input_interpretation, verb, result)
        i = response.find("?")
        if i != -1:
            response = response[i+1:].replace("is ", "").replace("(", "\n").replace(")", " ")
        response = [response]

    else:
        if len(others) > 0:
            for other in others:
                response.append(ask_wolfram(other))

    return response

def parse_is(txt):

   # if center_node:
   #     parent = parse_is(txt)
   #     if parent:
   #         parents.setdefault(center_node, [parent])

    txt = txt.lower()
    parent = None
    if " is " in txt:
        i = txt.find("is ")
        parent = txt[i+3:]
    return parent

def wolfram_to_nodes(query, lang="en-us"):
    parser = LILACSQuestionParser()
    responses = ask_wolfram(query)
    txt = query.lower().replace("the ", "").replace("an ", "").replace("a ", "")
    center_node, target_node, parents, synonims, midle, question = parser.process_entitys(txt)

    response = responses[0]


    txt = response.lower().replace("the ", "").replace("an ", "").replace("a ", "")
    if txt != "no answer":
        midle2, parents2, synonims2= parser.tag_from_dbpedia(txt)

        for parent in parents2:
            if parent not in parents:
                parents.setdefault(parent, parents2[parent])
        midle += midle2
        for synonim in synonims2:
            synonims.setdefault(synonim, synonims2[synonim])


    print "\nquestion: " + query
    print "answer: " + response
    print "question_type: " + question
    print "center_node: " + center_node
    print "target_node: " + target_node
    print "parents: " + str(parents)
    print "relevant_nodes: " + str(midle)
    print "synonims: " + str(synonims)

wolfram_to_nodes("frog")
wolfram_to_nodes("cat")
wolfram_to_nodes("human")
