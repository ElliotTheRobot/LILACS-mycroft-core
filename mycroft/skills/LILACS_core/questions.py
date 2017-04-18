# this file has standard helper functions to be imported when they are needed
# each of these answers a specific kind of question and takes a crawler as a param

# standard questions helper functions


def why_is_this_that(self, this, that, crawler=None):
    if crawler is None:
        return None
    crawler.explorer_crawl(this, that)
    nodes = crawler.crawl_path
    return nodes


def is_this_that(self, this, that, crawler=None):
    if crawler is None:
        return None
    flag = crawler.drunk_crawl(this, that)
    return flag


def examples_of_this(this, crawler=None):
    if crawler is None:
        return None
    crawler.drunk_crawl(this, "no target crawl", direction="childs")
    examples = []
    for example in crawler.crawled:
        if example != this:
            examples.append(example)
    return examples


def common_this_and_that( this, that, crawler=None):
    if crawler is None:
        return None
    crawler.drunk_crawl(this, "no target crawl")
    p_crawl = crawler.crawled
    common = []
    for node in p_crawl:
        flag = crawler.drunk_crawl(that, node)
        if flag:
            common.append(node)
    return common


def what_is_this(this, crawler=None):
    if crawler is None:
        return None
    crawler.drunk_crawl(this, "no target crawl", direction="parents")
    examples = []
    for example in crawler.crawled:
        examples.append(example)
    return examples
