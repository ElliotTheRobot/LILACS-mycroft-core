from mycroft.knowledge.services import KnowledgeBackend
from mycroft.util.log import getLogger
from mycroft.messagebus.message import Message

from os.path import abspath

import requests
import bs4

__author__ = 'jarbas'

logger = getLogger(abspath(__file__).split('/')[-2])


class WikiHowService(KnowledgeBackend):
    def __init__(self, config, emitter, name='wikihow'):
        self.config = config
        self.process = None
        self.emitter = emitter
        self.name = name
        self.emitter.on('WikihowKnowledgeAdquire', self._adquire)

    def _adquire(self, message=None):
        logger.info('WikihowKnowledge_Adquire')
        subject = message.data["subject"]
        if subject is None:
            logger.error("No subject to adquire knowledge about")
            return
        else:
            dict = {}
            # get knowledge about
            # TODO exceptions for erros
            try:
                how_to = self.how_to(subject)
                dict["wikihow"] = how_to
                self.emit_node_info(dict)
            except:
                logger.error("Could not parse wikihow for " + str(subject))


    def get_title(self, link):
        # get title of this how-to
        # print "Getting title of " + link
        title = link.replace("http://www.wikihow.com/", "").replace("-", " ")
        return title

    def search_wikihow(self, search_term):
        # print "Seaching wikihow for " + search_term
        search_url = "http://www.wikihow.com/wikiHowTo?search="
        search_term_query = search_term.replace(" ", "+")
        search_url += search_term_query
        # print search_url
        # open url
        html = self.get_html(search_url)
        soup = bs4.BeautifulSoup(html, "lxml")
        # parse for links
        list = []
        links = soup.findAll('a', attrs={'class': "result_link"})
        for link in links:
            url = "http:" + link.get('href')
            list.append(url)
        return list

    def get_html(self, url):
        headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0"}
        r = requests.get(url, headers=headers)
        html = r.text.encode("utf8")
        return html

    def get_steps(self, url):
        # open url
        html = self.get_html(url)
        soup = bs4.BeautifulSoup(html, "lxml")
        # get steps
        steps = []
        ex_steps = []
        step_html = soup.findAll("div", {"class": "step"})
        for html in step_html:
            trash = str(html.find("script"))
            trash = trash.replace("<script>", "").replace("</script>", "").replace(";", "")
            step = html.find("b")
            step = step.text
            ex_step = html.text.replace(trash, "")
            steps.append(step)
            ex_steps.append(ex_step)

        # get step pic
        pic_links = []
        pic_html = soup.findAll("a", {"class": "image lightbox"})
        for html in pic_html:
            i = str(html).find("data-src=")
            pic = str(html)[i:].replace('data-src="', "")
            i = pic.find('"')
            pic_links.append(pic[:i])

        return steps, ex_steps, pic_links

    def how_to(self, subject):
        how_tos = {}
        links = self.search_wikihow(subject)
        if links == []:
            print "No wikihow results"
            return
        for link in links:
            how_to = {}
            # how to title
            title = self.get_title(link)
            # get steps and pics
            steps, descript, pics = self.get_steps(link)
            how_to["title"] = title
            how_to["steps"] = steps
            how_to["detailed"] = descript
            how_to["pics"] = pics
            how_to["url"] = link
            how_tos[title] = how_to
        return how_tos

    def adquire(self, subject):
        logger.info('Call WikihowKnowledgeAdquire')
        self.emitter.emit(Message('WikihowKnowledgeAdquire', {"subject": subject}))

    def emit_node_info(self, info):
        # TODO emit node_info for node manager to update/create node
        for source in info:
            for key in info[source]:
                print "\n" + key + " : " + str(info[source][key])

    def stop(self):
        logger.info('WikihowKnowledge_Stop')
        if self.process:
            self.process.terminate()
            self.process = None



def load_service(base_config, emitter):
    backends = base_config.get('backends', [])
    services = [(b, backends[b]) for b in backends
                if backends[b]['type'] == 'wikihow']
    instances = [WikiHowService(s[1], emitter, s[0]) for s in services]
    return instances
