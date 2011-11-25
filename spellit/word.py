import collections
import datetime
import numbers
from google.appengine.ext import db
from .meaning import query_word


__all__ = ['Word']


class Word(db.Model):

    MEANING_UPDATE_PERIOD = datetime.timedelta(days=7)

    frequency = db.IntegerProperty(default=0, required=True, indexed=True)
    db_meaning = db.TextProperty(name='meaning')
    meaning_updated_at = db.DateTimeProperty()
    created_at = db.DateTimeProperty(auto_now_add=True, required=True)

    @classmethod
    def increment_frequencies(cls, frequencies):
        if not isinstance(frequencies, collections.Mapping):
            raise TypeError('expected mapping of {word: frequency}, not ' +
                            repr(frequencies))
        def incr(word, freq):
            word_object = cls.get_by_key_name(word)
            if word_object:
                word_object.frequency = word_object.frequency + freq
            else:
                word_object = cls(key_name=word, frequency=freq)
            word_object.put()
        for word in frequencies:
            freq = frequencies[word]
            if not isinstance(word, basestring):
                raise TypeError('key of mapping must be a word string, not ' +
                                repr(word))
            elif not isinstance(freq, numbers.Integral):
                raise TypeError('value of mapping must be a frequency '
                                'integer, not ' + repr(freq))
            db.run_in_transaction(incr, word, freq)

    @property
    def word(self):
        return self.key().name()

    def __iter__(self):
        return iter(self.word)

    def __len__(self):
        return len(self.word)

    def __contains__(self, character):
        return character in self.word

    def __getitem__(self, idx):
        return self.word[idx]

    def index(self, *args, **kwargs):
        return self.word.index(*args, **kwargs)

    def count(self, *args, **kwargs):
        return self.word.count(*args, **kwargs)

    def startswith(self, prefix, start=0, end=None):
        prefix = unicode(prefix)
        if end is None:
            end = len(self)
        return self.word.startswith(prefix, start, end)

    @property
    def meaning(self):
        if self.meaning_updated_at is None:
            expired = True
        else:
            expired_at = self.meaning_updated_at + self.MEANING_UPDATE_PERIOD
            expired = expired_at <= datetime.datetime.utcnow()
        if expired:
            self.update_meaning()
        return self.db_meaning

    @meaning.setter
    def meaning(self, value):
        self.db_meaning = value
        self.meaning_updated_at = datetime.datetime.utcnow()

    def update_meaning(self):
        self.meaning = query_word(self.word)

    def __unicode__(self):
        return self.word

    def __repr__(self):
        cls = type(self)
        return '<{0}.{1} {2!r}>'.format(cls.__module__, cls.__name__, self.word)

