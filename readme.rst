shorten
=======

A Python library for generating and revoking short keys.

It's gevent-safe, so you can use it with Gunicorn and Heroku (and
consequently Flask, Django, Pyramid). Currently, it is neither
threadsafe nor multiprocess safe.

Installation
------------

Install with pip:

.. code:: shell

   $ pip install shorten

If you want to run the tests, install the requirements in ``requirements.txt``:

.. code:: shell

   $ virtualenv --no-site-packages .python && source .python/bin/activate
   $ pip install -r requirements.txt

A Redis server, memcache server and the ``memcached`` development libraries are 
also required. Redis, memcache and gevent tests can be skipped by passing
``redis``, ``gevent`` or ``memcache`` to nose:

.. code:: shell

   $ nosetests tests -v -a !redis,!gevent,!memcache

Documentation
-------------

Full documentation is available at http://shorten.readthedocs.org/.

Quickstart
----------

Create a `store` which automatically generates keys for your values. The
key generation scheme depends upon the ``alphabet`` given.

.. code:: python

   from shorten import MemoryStore
   
   hexabet = '0123456789abcdef'
   store = MemoryStore(alphabet=hexabet)

   key, token = store.insert('aardvark')
  
   # '0'
   key
 
   for i in range(0, 255):
      key, token = store.insert('aardvark')

   # 'ff'
   key


Values can be deleted from the store by `revoking` them with the returned
revokation `token`. The default token is the same as the returned key.

.. code:: python

   key, token = store.insert('bonobo')

   # '1', since 'aardvark' has key '0'
   key

   del store[token]

   # False
   key in store


The included stores are gevent-safe, meaning that values can be inserted from
multiple greenlets without fear of duplicate keys.

.. code:: python

   import gevent
   from shorten import MemoryStore, 

   store = MemoryStore(alphabet=
   
 


Shuffling your alphabet produces a random-looking key every time, but the
order can easily be reconstructed from frequency counting and [Benford's law].

Never use short URLs to hide your data - use UUIDs or authentication instead.

The basics
----------

Make a store, which includes a key generator, token generator and object
for storing values:

.. code:: python

    from shorten import make_store
    import redis

    store = make_store('redis', redis=redis.Redis())

Map a short key to a long value. The short key and a revokation token
are returned:

.. code:: python

    # ('2111', '2111')
    key, token = store.insert('agitated aardvarks beg bonobos climbing caimans "dashing degu enjoy elk"')

Map multiple values to keys and revokation tokens from greenlets:

.. code:: python

    import gevent  
    from shorten import make_store

    values = [
      'aardvark', 
      'bonobo', 
      'caiman', 
      'degu', 
      'elk',
    ]
      
    store = make_store('memory')

    jobs = [gevent.spawn(store.insert, v) for v in values]   
    pairs = map(lambda j: j.value, gevent.joinall(jobs, timeout=2))

    # [('2111' '2111'), ('2112' '2112'), ('2114' '2114'), ('2113', '2113'), ('2115', ('2115')]
    print(pairs)

Revokation is built in, so keys can revoked easily as well:

.. code:: python

    from shorten import make_store

    store = make_store('memory')

    # ('2111', '2111')
    key, token = store.insert('aardvark')

    # 'aardvark'
    store[key]

    # True
    store.revoke(token)

    # KeyError
    store[key]

Formatters
~~~~~~~~~~

A ``Formatter`` is used to format the internal representation of a key
or token. This is useful for Redis and SQL databases, which often need
to prefix keys and columns in order to avoid clashes.

Any class or mixin with ``format_token`` and ``format_key`` methods can
be used.

.. code:: python

    import shorten
    import redis

    class RedisFormatter(object):

       counter = 'my:namespace:counter'

       def format_key(self, key):
          return 'my:namespace:key:{0}'.format(key)

       def format_token(self, token)
          return 'my:namespace:token:{0}'.format(token)

    formatter = RedisFormatter()
    store = make_store('redis', redis=redis.Redis(), redis_counter_key=formatter.counter, formatter=formatter)

    # Note that the keys returned are *not* prefixed
    # ('2111', '2111')
    key, token = store.insert('aardvark')

    # But the keys in redis *are* prefixed
    # 'aardvark' 
    redis.Redis().get(formatter.format_key(key))

Token generators
~~~~~~~~~~~~~~~~

By default, revokation tokens are created with the
``token.TokenGenerator`` class and the key itself is used.

Any class or mixin with a ``create_token`` method can be used as a token
generator.

.. code:: python
    
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
    

    from shorten import make_store

    store = make_store('memory', token_generator=GoogleTokenGenerator())
    
    # ('2111', 'mmoy-vvwg-trhc-uzqq')
    store.insert('aardvark')    

Alternate alphabets
~~~~~~~~~~~~~~~~~~~

Any zero-indexed iterable can be passed in as ``alphabet`` to a store or
the ``make_store`` function.

.. code:: python

    from shorten import make_store

    # Use an alternative alphabet with faces
    alphabet = [
      ':)', ':(', ';)', ';(', '>:)', ':D', ':x', ':X', ':O', '><', '<<', '>>', '^^', 'O_o',
    ]

    store = make_store('memory', alphabet=alphabet)

    values = [
      'aardvark', 
      'bonobo', 
      'caiman', 
      'degu', 
      'elk',
    ]

    keys = [store.insert(v)[0] for value in values]

    # [':(:):):)', ':(:):):(', ':(:):);)', ':(:):);(', ':(:):)>:)']
    print(keys)

Example
-------

For a working example of URL-shortening website, see ``example.py``.
