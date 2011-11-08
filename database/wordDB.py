'''
Created on Nov 8, 2011

@author: soyenze
'''
from google.appengine.ext import db

class Words(db.Model):
    word = db.StringProperty()
    freq = db.IntegerProperty()
    
class WordDBInterface():
    @staticmethod
    def insert(word):
        """
        get data for word
        if exist add just freq otherwise make new instance
        """
        
        obj = Words.get_by_key_name(word)
        
        if obj is None:
            obj = Words(key_name=word, word=word, freq=0)
        obj.freq += 1
        obj.put()
    
    @staticmethod
    def get_word_key(word):
        obj = Words.get_by_key_name(word)
        return obj.key()
    
    @staticmethod
    def allEntities():
        q = Words.all()
        objs = q.fetch(5)
        
        for obj in objs:
            yield obj.word, obj.freq
    
    @staticmethod
    def getWords(limit, offset=0):
        q = Words.all()
        objs = q.fetch(limit, offset)
        
        for obj in objs:
            yield obj.word

    @staticmethod
    def allWords():
        q = Words.all()
        objs = q.fetch(5)
        
        for obj in objs:
            yield obj.word