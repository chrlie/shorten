#!/usr/bin/env python

from shorten import __version__

try:
   from setuptools import setup
   kw = {}

except ImportError:
   from distutils.core import setup
   kw = {}

setup(
   name = 'shorten',
   packages = ['shorten'],
   version = __version__,
   description = 'A Python library for generating short URLs.',

   author = 'Charlie Liban',
   author_email = 'charlie@tyrannosaur.ca',
   maintainer='Charlie Liban',
   maintainer_email='charlie@tyrannosaur.ca',   

   url = 'https://github.com/tyrannosaur/shorten',
   download_url = 'https://github.com/tyrannosaur/shorten/zipball/master',
   keywords = ['redis','internet'],
   classifiers = [
      'Programming Language :: Python',
      'License :: OSI Approved :: MIT License',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Page Counters',
   ],

   license = 'MIT License',

   long_description = """\
Create your own URL-shortening functionality. It's gevent-safe, so you can use it
with Gunicorn and Flask/Django.

For example, you can create your own little shortening API:

::

  # For example, run as:
  # gunicorn -w 4 example:app

  import re
  from redis import Redis
  from flask import Flask, request, redirect, url_for, jsonify
  from werkzeug import iri_to_uri
  from shorten import shortener

  app = Flask(__name__)
  app_name = 'short.ur'

  redis = Redis()

  def is_url(string):
     return re.match('http(s){0,1}://.+\..+', string, re.I) is not None

  def to_short_token(key):
     return key.split(to_short_key(''), 1)[1]

  def to_short_key(token):
     return '{0}:key:{1}'.format(app_name, token)

  counter_key = '{0}:counter'.format(app_name)

  shortener = shortener('redis', redis=redis, 
                                 counter_key=counter_key, 
                                 formatter=to_short_key)

  @app.route('/')
  def shorten():
     try:
        url = request.args['u'].strip()
        if not is_url(url):
           return jsonify({'error' : 'not a valid url'})
        else:
           token = to_short_token(shortener.insert(url))
           return jsonify({'short' : url_for('bounce', token=token)})
     except KeyError, e:
        return jsonify({'error' : 'no url to shorten'})

  @app.route('/<token>')
  def bounce(token):
     try:
        token = to_short_key(token)
        return redirect(iri_to_uri(shortener[token]))
     except KeyError:
        return jsonify({'error' : 'no short url found'})
        
  if __name__ == '__main__':
     app.run('0.0.0.0')
""",
   **kw
)     
