from google.appengine.api import urlfetch
import lxml.html
import lxml.cssselect
import json
import re


__all__ = ['query_word', 'query_pageids', 'query_word_by_pageid']


LIST_API_URL = ('http://en.wiktionary.org/w/api.php?'
                'action=query&prop=revisions&rvprop=content&format=json&'
                'titles={0}')
WORD_API_URL = ('http://en.wiktionary.org/w/api.php?action=parse&format=json'
                '&pageid={0}')


def query_word(word):
    """Queries the word. It returns the meaning of the given word, string
    encoded html.

    """
    return query_word_by_pageid(query_pageids(word))


def query_pageids(word):
    """Queries the word from remote Wiktionary database and returns
    pageid of the word. When it cannot find the word, raises LookupError.

    """
    list_url = LIST_API_URL.format(word)
    result_list = urlfetch.fetch(list_url)
    assert result_list.status_code == 200, list_url + ' occurs an error'
    list_ = json.loads(result_list.content)
    for pageid in list_['query']['pages']:
        break
    else:
        raise LookupError('there no definition in wiktionary.org: ' +
                          repr(word))
    return pageid


def query_word_by_pageid(pageid):
    """Queries the word by Wiktionary pageid. It returns the meaning of
    the given pageid word as string encoded html.

    """
    url = WORD_API_URL.format(pageid)
    result = urlfetch.fetch(url)
    assert result.status_code == 200, url + ' occurs an error'
    page = json.loads(result.content)
    html = page['parse']['text'][u'*']
    tree = lxml.html.fromstring(html)
    sel = lxml.cssselect.CSSSelector('table#toc ul > li > a[href="#English"]')
    sel_result = sel(tree)
    if len(sel_result) < 1:
        raise LookupError('there seems no definition for English: ' +
                          repr(pageid))
    toc = sel_result[0].getparent()
    sel = lxml.cssselect.CSSSelector('ul > li > a')
    excludes = ['#Etymology', '#Alternative_forms', '#Pronunciation']
    for link in sel(toc):
        link = link.attrib['href']
        if not link.startswith('#'):
            continue
        elif link in excludes:
            continue
        break
    assert link.startswith('#')
    sel = lxml.cssselect.CSSSelector(link)
    heading = sel(tree)[0].getparent()
    def is_heading(el):
        return bool(re.match(r'^h[1-6]$', el.tag))
    content = heading.getnext()
    contents = []
    while not (content is None or is_heading(content)):
        content.rewrite_links(lambda _: None)
        contents.append(content)
        content = content.getnext()
    meaning = '\n'.join(lxml.html.tostring(el) for el in contents)
    return meaning

