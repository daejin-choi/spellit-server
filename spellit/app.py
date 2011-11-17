#!/usr/bin/env python
import json
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from .word import Word
from . import news


class BaseHandler(webapp.RequestHandler):

    def render(self, html, json_):
        t = self.request.accept.best_match(['text/html', 'application/json'])
        self.response.headers['Vary'] = 'Accept'
        if t:
            self.response.headers['Content-Type'] = t
        if t == 'application/json':
            json.dump(json_, self.response.out)
        elif t == 'text/html':
            self.response.out.write(html)
        else:
            self.error(406)


class WordListHandler(BaseHandler):

    def get(self):
        offset = self.request.get('offset', default_value=0)
        limit = self.request.get('limit', default_value=10)
        try:
            offset = int(offset)
            limit = int(limit)
        except ValueError:
            self.error(400)
        words = Word.all().order('__key__').fetch(limit=limit, offset=offset)
        self.render(html=words, json_=[w.key().name() for w in words])


class MeaningHandler(BaseHandler):

    def get(self, word):
        word = Word.get_by_key_name(word)
        if word:
            original = word.meaning_updated_at
            meaning = word.meaning
            if original != word.meaning_updated_at:
                word.put()
            return self.render(html=meaning, json_=meaning)
        self.error(404)


class CrawlWordHandler(BaseHandler):

    def get(self):
        NM = news.NewsManager()
        result = NM.GetNewsWords(2) # 2: number of news
        Word.increment_frequencies(result)


application = webapp.WSGIApplication([('/words', WordListHandler),
                                      ('/words/([^/]+)', MeaningHandler),
                                      ('/privacy/crawlword', CrawlWordHandler)],
                                     debug=True)

