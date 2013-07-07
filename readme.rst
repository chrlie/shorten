shorten
=======

Shorten is a `MIT licensed <http://opensource.org/licenses/MIT>`_ Python library
for storing your data with automatically generated keys. Use your choice of
backend: in-memory, Redis and Memcached are supported by default.

I made this library after being unable to find anything satisfactory for
URL shortening. Shorten contains no clever tricks or obfuscated schemes 
that produce unmaintainable code.

It's gevent-safe, so you can use it with Gunicorn and Heroku (and
consequently Flask, Django, Pyramid). Currently, it is neither
threadsafe nor multiprocess safe.

Installation
------------

Install with pip:

.. code:: sh

   $ pip install shorten

Testing
-------

If you want to run the tests, install the requirements in ``requirements.txt``:

.. code:: sh

   $ virtualenv --no-site-packages .python && source .python/bin/activate
   $ pip install -r requirements.txt

A Redis server, memcache server and the ``memcached`` development libraries are 
also required. Redis, memcache and gevent tests can be skipped by passing
``redis``, ``gevent`` or ``memcache`` to nose:

.. code:: sh

   $ nosetests tests -v -a !redis,!gevent,!memcache

Documentation
-------------

Full documentation is available at http://pythonhosted.org/shorten.

Quickstart
----------

Create a `store` which automatically generates `keys` for your values.

.. code:: python

   from shorten import MemoryStore
   
   store = MemoryStore()
   key, token = store.insert('aardvark')
  
   # True
   key in store

   # 'aardvark'
   store[key]


Values can be deleted from the store by `revoking` them with the returned
revokation `token`. The default token is the same as the returned key.

.. code:: python

   from shorten import MemoryStore
   
   store = MemoryStore()
   key, token = store.insert('bonobo')

   del store[token]

   # False
   key in store

   # KeyError
   store[key]


The included stores are gevent-safe, meaning that values can be inserted from
multiple greenlets without fear of duplicate keys.

.. code:: python

   import gevent
   
   from shorten import alphabets
   from shorten import MemoryStore

   values = (
      'aardvark',
      'bonobo',
      'caiman',
      'degu',
      'elk',
   )

   store = MemoryStore(alphabet=alphabets.HEX, start=9)
   jobs = [gevent.spawn(store.insert, value) for value in values]

   gevent.joinall(jobs)

   # '9'
   # 'a'
   # 'c'
   # 'b'
   # 'd'
   for job in jobs:
      key, token = job.value
      print(key)


Example
-------

For a working example of URL shortening website, see ``example.py``.
