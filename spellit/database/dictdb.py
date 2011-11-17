'''
Created on Nov 8, 2011

@author: soyenze
'''
from google.appengine.ext import db


class Dictionary(db.Model):
    word_key = db.ReferenceProperty()
    freq = db.StringProperty(multiline=True)

class DictInterface():

    def insert(self, word_key, desc):
        """
        get data for word
        if exist add just freq otherwise make new instance
        """

        q = Dictionary.all().filter(word_key,  word_key)
        obj = q.get()

        if obj is not None:
            obj.desc = desc
            obj.put()

