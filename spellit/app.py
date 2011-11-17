#!/usr/bin/env python
import json
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from spellit.database import worddb
from spellit import news


class BaseHandler(webapp.RequestHandler):

    def render(self, html, json):
        t = self.request.accept.best_match(['text/html', 'application/json'])
        self.response.headers['Vary'] = 'Accept'
        if t:
            self.response.headers['Content-Type'] = t
        if t == 'application/json':
            json.dump(self.response.out, json)
        elif t == 'text/html':
            self.response.out.write(html)
        else:
            self.error(406)


class WordListHandler(BaseHandler):

    def get(self):
        offset = self.request.get('offset', default_value=0)
        limit = self.request.get('limit', default_value=10)

        offset = int(offset)
        limit = int(limit)

        word_db_handle = worddb.WordDBInterface

        words = list(word_db_handle.getWords(int(limit), int(offset)))
        self.render(html=words, json=words)


class MeaningHandler(BaseHandler):

    def get(self):
        word = self.request.get('word')

        url = ('http://en.wiktionary.org/w/'
               'api.php?action=query&prop=revisions&rvprop=content&format=json')
        url = url + '&titles=' + str(word)

        result = urlfetch.fetch(url)

        if result.status_code != 200:
            return

        obj = json.loads(result.content)
        pagedata = obj['query']['pages']
        pages = pagedata.keys()

        # temporarily just use only first retrieved page
        if len(pages) == 0:
            # raise no result error
            return

        strdata = pagedata[pages[0]]['revisions'][0][u'*']
        #self.response.out.write(strdata)

        for match in TOKEN_TYPE_RE.finditer(strdata):
            realdata = strdata[match.start():match.end()-1].encode('utf-8')
            self.response.out.write(realdata)
            break


class WordHandler(BaseHandler):

    def get(self):
        strwords = self.request.get('words')
        strwords = str(strwords)

        words = strwords.split('|')

        word_db_handle = worddb.WordDBInterface
        for word in words:
            word_db_handle.insert(word)


class CrawlWordHandler(BaseHandler):

    def get(self):
        NM = news.NewsManager()
        result = NM.GetNewsWords(2) # 2: number of news

        word_db_handle = worddb.WordDBInterface
        word_db_handle.insertWords(result)


application = webapp.WSGIApplication([('/words', WordListHandler), 
                                      ('/meaning', MeaningHandler),
                                      ('/privacy/insertword', WordHandler),
                                      ('/privacy/crawlword', CrawlWordHandler)],
                                     debug=True)
