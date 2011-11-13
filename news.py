'''
Created on Nov 11, 2011

@author: soyenze
'''

import lxml.html
import lxml.cssselect
import feedparser

NEWS_TAG = ['title', 'guid', 'link', 'description', 'pubDate']

class NewsManager(object):

    def __init__(self):
        self.wordFrequency = {}

    def parseFeed(self, content, maxlength=20):
        
        startidx = 0
        endidx = 0
        retcount = 0
        
        while( True ):
            startidx = content.find('<item>', endidx)
            endidx = content.find('</item>', startidx)
            
            if startidx == -1 or endidx == -1 or retcount >= maxlength:
                break
            startidx = startidx + len('<item>')
            
            item = content[startidx:endidx]
            retcount += 1
            
            sentences = list(self.crawlWords(item))
            
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

        print self.wordFrequency
        
    def crawlWords(self, content):
        feedDict = {}
        
        for tag in NEWS_TAG:
            startTag = '<' + tag + '>'
            endTag = '</' + tag + '>'
            startidx = content.find(startTag) + len(startTag)
            endidx = content.find(endTag)
            
            feedDict[tag] = content[startidx:endidx]
        
        print feedDict['link'], '\n'
        
        html = lxml.html.parse(feedDict['link'])
        sel = lxml.cssselect.CSSSelector('div.cnn_strycntntlft > p')
        paras = sel(html)
        
        for p in paras:
            if p.text:
                yield p.text