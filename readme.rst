shorten
=======

A Python library for generating and revoking short keys.

It's gevent-safe, so you can use it with Gunicorn and Heroku (and
consequently Flask, Django, Pyramid). Currently, it is neither
threadsafe nor multiprocess safe.

Installation
------------

Install with pip: ``pip install shorten``

If you want to run the tests, ensure ``nose``, ``redis`` and ``gevent``
are installed with ``pip install nose redis gevent``, then:

.. code:: shell

    nosetests tests.py -v

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
or token. This is useful for Redis and traditional databases, which need
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

    # ('my:namespace:key:2111', 'my:namespace:key:2111')
    key, token = store.insert('aardvark')

Token generators
~~~~~~~~~~~~~~~~

By default, revokation tokens are created with the
``token.TokenGenerator`` class and the key itself is used.

Any class or mixin with a ``create_token`` method can be used as a token
generator.

Alternate alphabets
~~~~~~~~~~~~~~~~~~~

Any zero-indexed iterable can be passed in as ``alphabet`` to a store or
the ``make_store`` function.

.. code:: python

    from shorten import make_store

    # Use an alternative alphabet with faces
    alphabet = [
      ':)', ':(', ';)', ';(', '>:)', ':D', ':x', ':X', ':|', ':O', '><', '<<', '>>', '^^', 'O_o',
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
