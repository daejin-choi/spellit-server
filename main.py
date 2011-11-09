#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from database import wordDB
from google.appengine.api import urlfetch
from django.utils import simplejson

import re
TOKEN_TYPE_RE = re.compile(r'''
    ( ={2,10}Noun={2,10}[^=]+= ) |
    ( ={2,10}Pronoun={2,10}[^=]+= ) |
    ( ={2,10}Adjective={2,10}[^=]+= ) |
    ( ={2,10}Adverb={2,10}[^=]+= ) |
    ( ={2,10}Verb={2,10}[^=]+= ) |
    ( ={2,10}Preposition={2,10}[^=]+= ) |
    ( ={2,10}Conjunction={2,10}[^=]+= ) |
    ( ={2,10}Interjection={2,10}[^=]+= )
''', re.VERBOSE)

def ShowErrorScreen(handler, errormsg):
    handler.response.header = { 'Content-Type':'text/html'}
    handler.response.out.write(errormsg)


class WordListHandler(webapp.RequestHandler):
    def get(self):
        """
        content_type = self.request.headers['Content_Type']
        
        if content_type != 'application/json':
            ShowErrorScreen(self, 'Invalid access')
            return
        """
        offset = self.request.get('offset', default_value=0)
        limit = self.request.get('limit', default_value=10)
        
        offset = int(offset)
        limit = int(limit)
        
        word_db_handle = wordDB.WordDBInterface
        #word_db_handle.insert('11111')
        
        words = list(word_db_handle.getWords(int(limit), int(offset)))
        header = {'Content-Type':'applications/json'}
        
        self.response.header = header
        self.response.out.write(words)
        
class MeaningHandler(webapp.RequestHandler):
    def get(self):
        """
        content_type = self.request.headers['Content_Type']
        
        if content_type != 'application/json':
            ShowErrorScreen(self, 'Invalid access')
            return
        """
        word = self.request.get('word')
        
        url = 'http://en.wiktionary.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json'
        url = url + '&titles=' + str(word)
    
        result = urlfetch.fetch(url)
        
        if result.status_code != 200:
            return
        
        obj = simplejson.loads(result.content)
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
        
        
class WordHandler(webapp.RequestHandler):
    def get(self):
        strwords = self.request.get('words')
        strwords = str(strwords)
        
        words = strwords.split('|')
        
        word_db_handle = wordDB.WordDBInterface
        map( lambda x:word_db_handle.insert(x), words)
        
def main():
    application = webapp.WSGIApplication([('/words', WordListHandler), 
                                          ('/meaning', MeaningHandler),
                                          ('/privacy/insertword', WordHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
