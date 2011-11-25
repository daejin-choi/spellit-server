#!/usr/bin/env python
import json
import random
import hashlib
import hmac
import base64
import datetime
from google.appengine.api import urlfetch
from flask import Flask, abort, g, redirect, render_template, request, session
from .word import Word
from .user import User
from . import news


app = Flask(__name__)
app.secret_key = 'dofiadiovasdiovjaosdcjviasdjvcewj'
facebook_secret = 'cb1b72a8ccb11253bcef244fbccbd7da'


@app.before_request
def verify_sign():
    if request.path != '/':
        try:
            g.user = session['fbid']
        except KeyError:
            abort(403)


@app.context_processor
def inject_user():
    return {'current_user': current_user()}


def current_user():
    return User.get_by_key_name(session['fbid'])


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
    word = Word.get_by_key_name('about')
    current_user().encrypt_word(word)
    return render_template('home.html', next_word=word)


@app.route('/plays/<word>')
def plays(word):
    try:
        started_at = session['started_at']
    except KeyError:
        started_at = datetime.datetime.utcnow()
        session['started_at'] = started_at
    word = current_user().decrypt_word(str(word))
    character_set = word.character_set
    return render_template('plays.html', word=word, character_set=character_set)


@app.route('/plays/playing')
def playing():
    btn1 = request.values.get('btn1')
    word = session['word']
    correct_spell = session['correct_spell']

    len_correct_spell = len(correct_spell)
    len_word = len(word)
    if word[:len_correct_spell+1] == correct_spell + btn1:
        session['correct_spell'] = session['correct_spell'] + btn1
        session['word'] = session['correct_spell']

        if len_correct_spell + 1 + 5 > len_word:
            return ''
        return word[len_correct_spell + 1 + 5]
    return btn1


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

@app.route('/privacy/crawlword')
def crawlword():
    NM = news.NewsManager()
    result = NM.GetNewsWords(2) # 2: number of news
    Word.increment_frequencies(result)

    return ''

