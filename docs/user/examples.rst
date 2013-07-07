Examples
========

.. _token-gen-example:

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

Imitate goo.gl, bit.ly, tinyurl and countless other URL shortening
services in under a hundred lines of code.

`Flask <https://pypi.python.org/pypi/flask/>`_,
`rfc3987 <https://pypi.python.org/pypi/rfc3987/>`_ and
`redis <https://pypi.python.org/pypi/redis/>`_ are required.

.. code:: sh

   $ virtualenv --no-site-packages .python && source .python/bin/activate
   $ pip install flask rfc3987 redis

Our API will read in a URL from a POST variable and return JSON containing
the shortened link and the revokation URL. Proper HTTP response codes
are also returned - 400 for errors and 200 for successful operations.

Let's set up the Flask skeleton code:

::

   from flask import Flask, request, redirect, url_for
   from flask import jsonify as _jsonify

   def jsonify(obj, status_code=200):
      obj['status'] = 'error' if 'error' in obj else 'okay'
      res = _jsonify(obj)
      res.status_code = status_code
      return res

   app = Flask(__name__)

   @app.route('/', methods=['POST'])
   def shorten():
      pass
   
   @app.route('/', methods=['GET'])
   def bounce():
      pass

   @app.route('/r', methods=['POST'])
   def revoke(token):
      pass


After creating a Redis connection, the store should be created with a 
minimum key length (as to not conflict with site URLs) and a URL-safe 
alphabet:

::

   import redis
   from shorten import RedisStore, NamespacedFormatter, UUIDTokenGenerator
   from shorten import alphabets

   redis_client = redis.Redis()
   formatter = NamespacedFormatter('shorten')
   token_gen = UUIDTokenGenerator()

   store = RedisStore(redis_client=redis_client, 
      min_length=3,
      counter_key='shorten:counter_key',
      formatter=formatter,
      token_gen=token_gen,
      alphabet=alphabets.URLSAFE_DISSIMILAR)


Now the endpoint functions can be filled out:

::

   from rfc3987 import parse
   from werkzeug import iri_to_uri

   from shorten import RevokeError

   def valid_url(url):
      return bool(parse(url, rule='URI_reference'))

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


The above code can be found in ``example.py``. To run the server, 
install gevent and Gunicorn, then run Gunicorn in the same directory
as ``example.py``:

.. code:: sh
   
   $ pip install gunicorn gevent
   $ gunicorn example:app -b 0.0.0.0:5000 -w 3 -k gevent_wsgi

