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

def ShowErrorScreen(handler, errormsg):
    handler.response.header = { 'Content-Type':'text/html'}
    handler.response.out.write(errormsg)


class InterfaceHandler(webapp.RequestHandler):
    def get(self):
        
        content_type = self.request.headers['Content_Type']
        
        if content_type != 'application/json':
            ShowErrorScreen(self, 'Invalid access')
            return
        
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
        
class WordHandler(webapp.RequestHandler):
    def get(self):
        strwords = self.request.get('words')
        strwords = str(strwords)
        
        words = strwords.split('|')
        
        word_db_handle = wordDB.WordDBInterface
        map( lambda x:word_db_handle.insert(x), words)
        
def main():
    application = webapp.WSGIApplication([('/words', InterfaceHandler), 
                                          ('/privacy/insertword', WordHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
