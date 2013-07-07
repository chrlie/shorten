Examples
========

A Mock Google Token Generator
-----------------------------

Transform a UUID into a form that looks similar to Google temporary
passwords.

::

   from uuid import uuid4
   from shorten.key import bx_encode

   def group(string, n):
      return [string[i:i+n] for i in range(0, len(string), n)]

   class GoogleTokenGenerator(object):
      """\
      This will produce 16 character alphabetic revokation tokens similar
      to the ones Google uses for its application-specific passwords.

      Google tokens are of the form:

         xxxx-xxxx-xxxx-xxxx

      with alphabetic characters only.
      """

      alphabet = 'abcdefghijklmnopqrstuvwxyz'

      def create_token(self, key):
         token_length = 16
         group_size = 4
         groups = token_length/group_size

         # Generate a random UUID
         uuid = uuid4()

         # Convert it to a number with the given alphabet,
         # padding with the 0-symbol as needed)
         token = shorten.key.bx_encode(int(uuid.hex, 16), self.alphabet)
         token = token.rjust(token_length, self.alphabet[0])

         return '-'.join(group(token, group_size)[:groups])


   from shorten import MemoryStore

   store = MemoryStore(token_generator=GoogleTokenGenerator())
   key, token = store.insert('aardvark')

   # 'mmoy-vvwg-trhc-uzqq'
   token


URL Shortening Service
----------------------

Imitate goo.gl, bit.ly, tw.tr and countless other URL shortening
services in under a hundred lines of code.

::

   from rfc3987 import parse
   from flask import Flask, jsonify as _jsonify

   app = Flask(__name__)

   def jsonify(obj, status_code=200):
      obj['status'] = 'error' if 'error' in obj else 'okay'
      res = _jsonify(obj)
      res.status_code = status_code
      return res

   @app.route('/', methods=['POST'])
   def shorten():
      uri = request.body()
      parsed_uri = parse(url, rule='URI_reference')

      if parsed_uri:
         key, token = store.insert(uri)

         url = url_for('resolve', key=key, _external=True)
         revoke = url_for('revoke', token=token, _external=True)
         return jsonify({'url': url, 'revoke': revoke})
      else:
         return jsonify({'error': 'invalid url'}, 400)

   @app.route('/<key>', methods=['GET'])
   def resolve(key):
      try:
         uri = store[key]
         return redirect(iri_to_uri(uri))
      except KeyError as e:
         return jsonify({'error': 'url not found'}, 400)
   
Running with gunicorn 


