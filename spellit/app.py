#!/usr/bin/env python
import json
import random
import hashlib
import hmac
import base64
import datetime
from google.appengine.api import urlfetch
from flask import (Flask, abort, flash, g, redirect, render_template, request,
                   session, url_for)
from .word import Word
from .user import User
from . import news


app = Flask(__name__)
app.secret_key = 'dofiadiovasdiovjaosdcjviasdjvcewj'
facebook_secret = 'cb1b72a8ccb11253bcef244fbccbd7da'


@app.before_request
def verify_sign():
    if request.path != '/' and request.path != '/tasks/crawlword':
        try:
            g.user = session['fbid']
        except KeyError:
            abort(403)


@app.context_processor
def inject_user():
    return {'current_user': current_user()}


@app.template_filter('safeword')
def urlize_word(word):
    try:
        return current_user().encrypt_word(word)
    except OverflowError:
        print word
        raise


def current_user():
    return User.get_by_key_name(session['fbid'])


def get_new_word():
    record = session.get('record', frozenset())
    while True:
        Words = Word.all()
        next_word = Words[random.randint(0, Words.count() - 1)]
        if next_word not in record:
            break
    return next_word


@app.route('/')
def redirect_to_fb_app():
    return redirect('http://apps.facebook.com/spell-it/')


@app.route('/', methods=['POST'])
def home():
    def base64_url_decode(input_):
        if not isinstance(input_, str):
            input_ = str(input_)
        padding_factor = (4 - len(input_) % 4) % 4
        input_ += '=' * padding_factor
        return base64.urlsafe_b64decode(input_)
    try:
        signed_request = request.form['signed_request']
    except KeyError:
        return redirect_to_fb_app()
    sig, payload = signed_request.split('.', 1)
    sig = base64_url_decode(sig)
    ver = hmac.new(facebook_secret, payload, hashlib.sha256).digest()
    if sig != ver:
        abort(400)
    obj = base64_url_decode(payload)
    obj = json.loads(obj)
    url = 'https://graph.facebook.com/{0}?access_token={1}'
    res = urlfetch.fetch(url.format(obj['user_id'], obj['oauth_token']),
                         validate_certificate=False)
    user = json.loads(res.content)
    user = User.get_or_insert(obj['user_id'], name=user['name'])
    session['fbid'] = obj['user_id']
    session['access_token'] = obj['oauth_token']
    word = get_new_word()
    return render_template('home.html', next_word=word)


@app.route('/plays/<word>')
@app.route('/plays/<word>/<trial>')
def plays(word, trial=''):
    word = current_user().decrypt_word(str(word))
    #assert word.startswith(trial), 'word = %r, trial = %r' % (word, trial)
    if not word.startswith(trial):
        flash('You are Incorrect, please try with another spelling')
        if len(trial) != 0:
            trial = trial[:-1]
        return redirect(url_for('plays', word=urlize_word(word),
                                         trial=trial))
    if word.word == trial:
        record = session.get('record', frozenset())
        session['record'] = record.union(frozenset([word]))

        while True:
            Words = Word.all()
            next_word = Words[random.randint(0, Words.count() - 1)]
            if next_word not in session['record']:
                break
        return redirect(url_for('plays', word=urlize_word(next_word)))
    len_diff = len(word) - len(trial)
    replace_word = trial + '_ ' * len_diff
    meaning = word.meaning.replace(word.word, replace_word)
    character_set = list(frozenset(word[len(trial):]))
    random.shuffle(character_set)
    return render_template('plays.html',
                           word=word, character_set=character_set, trial=trial,
                           meaning=meaning)


@app.route('/end')
def end():
    session['word'] = ''
    session['correct_spell'] = ''
    return render_template('end.html', time=3600)


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

@app.route('/tasks/crawlword')
def crawlword():
    NM = news.NewsManager()
    result = NM.GetNewsWords(5) # 5: number of news
    Word.increment_frequencies(result)

    return ''


