"""
Create your own little shortening API.

For example:
   gunicorn -w 4 example:app
"""

import redis

from rfc3987 import parse

from flask import Flask, request, redirect, url_for
from flask import jsonify as _jsonify

from werkzeug import iri_to_uri

from shorten import RedisStore, NamespacedFormatter, UUIDTokenGenerator, RevokeError
from shorten import alphabets

def jsonify(obj, status_code=200):
   obj['status'] = 'error' if 'error' in obj else 'okay'
   res = _jsonify(obj)
   res.status_code = status_code
   return res

def valid_url(url):
   p = parse(url, rule='URI_reference')
   return all(p['scheme'], p['authority'], p['path'])

app = Flask(__name__)

redis_client = redis.Redis()
formatter = NamespacedFormatter('shorten')
token_gen = UUIDTokenGenerator()

store = RedisStore(redis_client=redis_client, 
   min_length=3,
   counter_key='shorten:counter_key',
   formatter=formatter,
   token_gen=token_gen,
   alphabet=alphabets.URLSAFE_DISSIMILAR)

@app.route('/', methods=['POST'])
def shorten():
   url = request.form['url'].strip()

   if not valid_url(url):
      return jsonify({'error': str(e)}, 400)

   key, token = store.insert(url)

   url = url_for('bounce', key=key, _external=True)
   revoke = url_for('revoke', token=token, _external=True)
   
   return jsonify({'url': url, 'revoke': revoke})

@app.route('/<key>', methods=['GET'])
def bounce(key):
   try:
      uri = store[key]
      return redirect(iri_to_uri(uri))
   except KeyError as e:
      return jsonify({'error': 'url not found'}, 400)

@app.route('/r/<token>', methods=['POST'])
def revoke(token):
   try:
      store.revoke(token)
   except RevokeError as e:
      return jsonify({'error': e}, 400)

   
if __name__ == '__main__':
   app.run('0.0.0.0')
