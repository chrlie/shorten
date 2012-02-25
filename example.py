"""
Create your own little shortening API.
"""

from flask import Flask, request, redirect, url_for, jsonify
from werkzeug import iri_to_uri
from shorten import Shortener

app = Flask(__name__)
shortener = Shortener(min_length=4)

@app.route('/')
def shorten():
   try:      
      url = request.args['u']
      short = url_for('bounce', url=shortener.insert(url))
      return jsonify({'short' : short})
   except KeyError:
      return jsonify({'error' : 'no url to shorten'})

@app.route('/<url>')
def bounce(url):
   try:
      return redirect(iri_to_uri(shortener[url]))
   except KeyError:
      return jsonify({'error' : 'no short url found'})
      
if __name__ == '__main__':
   app.run('0.0.0.0')
