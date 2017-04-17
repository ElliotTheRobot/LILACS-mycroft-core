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

__author__ = 'seanfitz'

LOG = getLogger(__name__)


class EnglishQuestionParser(object):
    """
    Poor-man's english question parser. Not even close to conclusive, but
    appears to construct some decent w|a queries and responses.
    """

    def __init__(self):
        self.regexes = [
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|whose) "
                "(?P<Query1>.*) (?P<QuestionVerb>is|are|was|were) "
                "(?P<Query2>.*)"),
            re.compile(
                ".*(?P<QuestionWord>who|what|when|where|why|which|how) "
                "(?P<QuestionVerb>\w+) (?P<Query>.*)")
        ]

    def _normalize(self, groupdict):
        if 'Query' in groupdict:
            return groupdict
        elif 'Query1' and 'Query2' in groupdict:
            return {
                'QuestionWord': groupdict.get('QuestionWord'),
                'QuestionVerb': groupdict.get('QuestionVerb'),
                'Query': ' '.join([groupdict.get('Query1'), groupdict.get(
                    'Query2')])
            }

    def parse(self, utterance):
        for regex in self.regexes:
            match = regex.match(utterance)
            if match:
                return self._normalize(match.groupdict())
        return None


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

question_parser = EnglishQuestionParser()

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


print ask_wolfram("how much wood can a woodchuck chuck")
