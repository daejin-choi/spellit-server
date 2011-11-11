'''
Created on Nov 11, 2011

@author: soyenze
'''

from google.appengine.api import urlfetch

NEWS_TAG = ['title', 'guid', 'link', 'description', 'pubDate']

class NewsManager:
    def __init__(self):
        self.wordFrequency = {}
        
    def parseFeed(self, content, maxlength=20):
        
        startidx = endidx = 0
        retcount = 0
        
        while( True ):
            startidx = content.find('<item>', endidx)
            endidx = content.find('</item>', startidx)
            
            if startidx == -1 or endidx == -1 or retcount >= maxlength:
                break
            startidx = startidx + len('<item>')
            
            item = content[startidx:endidx]
            retcount += 1
            
            sentences = list( self.crawlWords(item) )
            
            def extractWords( content ):
                words = content.split(' ')
                
                def storeFrequncy( word ):
                    word.strip()
                    
                    # stopwords process
                    
                    if self.wordFrequency.has_key(word):
                        self.wordFrequency[word] += 1
                    else:
                        self.wordFrequency[word] = 1
                
                map( lambda x:storeFrequncy(x), words)
                
            map( lambda x:extractWords(x), sentences)

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
        
        result = urlfetch.Fetch(feedDict['link'])
        
        if result.status_code != 200:
            return
        
        content = result.content
        
        startDividx = content.find('cnn_strycntntlft')

        if startDividx != -1:
            content = content[startDividx+2+len('cnn_strycntntlft'):]
            
            startDividx = endDividx = 0
            
            while( True ):
                startDividx = content.find('<div', startDividx)
                endDividx = content.find('</div>', endDividx)
                
                if startDividx == -1 or endDividx < startDividx:
                    break
                startDividx += 4
                endDividx += 6

            content = content[:endDividx]
            startidx = endidx = 0
            
            while( True ):
                startidx = content.find('<p>', endidx )
                endidx = content.find('</p>', startidx )
                
                if startidx == -1 or endidx == -1:
                    break
                yield content[startidx+3:endidx]
