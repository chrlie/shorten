"""
Create your own little shortening API.

For example:
   gunicorn -w 4 example:app
"""

import re

from redis import Redis
from flask import Flask, request, redirect, url_for, jsonify as _jsonify
from werkzeug import iri_to_uri

from shorten import make_store
from shorten.token import UUIDTokenGenerator

app = Flask(__name__)
app_name = 'short.ur'

redis = Redis()

def okay(obj=None):   
   default = {'status': 'okay'}
   default.update(obj or {})
   return _jsonify(default)

def error(obj, error_code=400):
   default = {'status': 'error'}
   default.update(obj)
   res = _jsonify(default)
   res.error_code = error_code
   return res

def valid_url(string):
   # TODO: Don't allow anything redirecting to the site itself  
   return re.match('http(s){0,1}://.+\..+', string, re.I) is not None

class RedisFormatter(object):

   redis_namespace = app_name   

   def format_key(self, key):
      return '{0}:key:{1}'.format(self.redis_namespace, key)

   def format_token(self, token):
      return '{0}:token:{1}'.format(self.redis_namespace, token)

   @property
   def counter_key(self):
      return '{0}:counter'.format(self.redis_namespace)

formatter = RedisFormatter()
token_gen = UUIDTokenGenerator()
store = make_store('redis', redis=redis, redis_counter_key=formatter.counter_key, \
                            token_generator=token_gen, formatter=formatter)

@app.route('/')
def shorten():
   try:
      url = request.args['u'].strip()

      if not valid_url(url):
         return error({'error': 'Not a valid url.'})
      else:
         key, token = store.insert(url)
         short_url = url_for('bounce', key=key, _external=True)
         revoke_url = url_for('revoke', token=token, _external=True)

         return okay({'short_url': short_url, 'revoke_url': revoke_url})

   except KeyError as e:
      return error({'error': 'No url provided.'})

@app.route('/<key>')
def bounce(key):
   try:     
      url = store[key]
      return redirect(iri_to_uri(url))

   except KeyError:
      return error({'error': 'No URL found.'})

@app.route('/r/<token>')
def revoke(token=None):  
   try:
      store.revoke(token)
      return okay()

   except KeyError as e:
      return error({'error': 'Could not revoke.'})
      
if __name__ == '__main__':
   app.run('0.0.0.0')
