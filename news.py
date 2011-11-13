'''
Created on Nov 11, 2011

@author: soyenze
'''

import lxml.html
import lxml.cssselect
import feedparser
from google.appengine.api import urlfetch

FEED_URL = "http://rss.cnn.com/rss/edition.rss"
NEWS_TAG = "div.cnn_strycntntlft > p"

class NewsManager(object):

    def __init__(self):
        self.wordFrequency = {}

    def GetNewsWords(self, maxlength=20):
        
        print 11
        retcount = 0
        feed = urlfetch.Fetch(FEED_URL)
        result = feedparser.parse(feed.content)
        
        if 'entries' in result:
            for item in result['entries']:
                if retcount >= maxlength:
                    break
                if item and item['links'] and item['links'][0]:
                    sentences = list(self.crawlWords(item['links'][0]))
                    retcount += 1
                
                def extractWords(content):
                    words = content.split(' ')
                    
                    def storeFrequncy( word ):
                        word.strip()
                        # stopwords process
                        if word in self.wordFrequency:
                            self.wordFrequency[word] += 1
                        else:
                            self.wordFrequency[word] = 1
                    
                    map(storeFrequncy, words)
                
                map(extractWords, sentences)
        
        return self.wordFrequency
        
            
    def crawlWords(self, newslink):
        print newslink['href']
        html = lxml.html.parse(newslink['href'])
        sel = lxml.cssselect.CSSSelector(NEWS_TAG)
        paras = sel(html)

        for p in paras:
            if p.text:
                yield p.text
        