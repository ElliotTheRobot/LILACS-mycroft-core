import requests
import bs4


def get_title(link):
    # get title of this how-to
    # print "Getting title of " + link
    title = link.replace("http://www.wikihow.com/", "").replace("-", " ")
    return title


def search_wikihow(search_term):
    #print "Seaching wikihow for " + search_term
    search_url = "http://www.wikihow.com/wikiHowTo?search="
    search_term_query = search_term.replace(" ", "+")
    search_url += search_term_query
    # print search_url
    # open url
    html = get_html(search_url)
    soup = bs4.BeautifulSoup(html, "lxml")
    # parse for links
    list = []
    links = soup.findAll('a', attrs={'class': "result_link"})
    for link in links:
        url = "http:" + link.get('href')
        list.append(url)
    return list


def get_html(url):
    headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0"}
    r = requests.get(url, headers=headers)
    html = r.text.encode("utf8")
    return html


def get_steps(url):
    # open url
    html = get_html(url)
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


def how_to(subject):
    how_tos = {}
    links = search_wikihow(subject)
    if links == []:
        print "No wikihow results"
        return
    for link in links:
        how_to = {}
        # how to title
        title = get_title(link)
        # get steps and pics
        steps, descript, pics = get_steps(link)
        how_to["title"] = title
        how_to["steps"] = steps
        how_to["detailed"] = descript
        how_to["pics"] = pics
        how_to["url"] = link
        how_tos[title] = how_to
    return how_tos


def main():
    how_tos = how_to("boil an egg")
    for how in how_tos:
        print "How to " + how
        i = 0
        for step in how_tos[how]["steps"]:
            print "step " + str(i) + " : " + step
            print how_tos[how]["pics"][i]
            i += 1
        break