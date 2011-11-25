#!/usr/bin/env python
import json
from flask import Flask, abort, request
from .word import Word
from . import news


app = Flask(__name__)
app.secret_key = 'dofiadiovasdiovjaosdcjviasdjvcewj'


@app.route('/words/')
def words():
    offset = request.values.get('offset', type=int, default=0)
    limit = request.values.get('limit', type=int, default=10)
    words = Word.all().order('__key__').fetch(limit=limit, offset=offset)
    return json.dumps([w.key().name() for w in words])


@app.route('/words/<word>')
def meaning(word):
    word = Word.get_by_key_name(word)
    if word:
        original = word.meaning_updated_at
        meaning = word.meaning
        if original != word.meaning_updated_at:
            word.put()
        return meaning
    else:
        abort(400)

@app.route('/privacy/crawlword')
def crawlword():
    NM = news.NewsManager()
    result = NM.GetNewsWords(2) # 2: number of news
    Word.increment_frequencies(result)

    return ''

