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
   keywords = ['redis','internet','url'],
   classifiers = [
      'Programming Language :: Python',
      'License :: OSI Approved :: MIT License',
      'Topic :: Internet :: WWW/HTTP',
   ],

   license = 'MIT License',

   long_description = """\
shorten
=======

A Python library for generating short URLs.

It’s gevent-safe, so you can use it with Gunicorn (and consequently
Flask, Django and Pyramid). Currently, it is neither threadsafe nor
multiprocess safe.

Installation
------------

Install with pip: ``pip install shorten``

If you want to run the tests, ensure ``nose``, ``redis`` and ``gevent``
are installed with ``pip install nose redis gevent``, then:

::

    nosetests tests.py -v

The basics
----------

Make a shortener:

::

    import shorten
    import redis

    shortener = shorten.shortener('redis', redis=redis.Redis())

Map a short key to a long value:

::

    # '2111'
    key = shortener.insert('http://mitpress.mit.edu/sicp/full-text/book/book.html')

Map multiple keys and values from greenlets:

::

    import gevent   

    values = [
      'aardvark', 
      'bonobo', 
      'caiman', 
      'degu', 
      'elk',
    ]
      
    jobs = [gevent.spawn(shortener.insert, v) for v in values]   
    keys = map(lambda j: j.value, gevent.joinall(jobs, timeout=2))

    # ['2111', '2112', '2114', '2113', '2115']
    print(keys)

If you wish to store the keys with some sort of prefix, pass in a
``formatter`` function when a ``KeyStore`` is created:

::

    import shorten
    import redis

    def to_key_format(token):
      return 'my:namespace:key:{0}'.format(token)

    shortener = shorten.shortener('redis', redis=redis.Redis(), formatter=to_key_format)

    # 'my:namespace:key:2111'
    key = shortener.insert('http://mitpress.mit.edu/sicp/full-text/book/book.html')

Custom alphabets of symbols (any 0-index based iterable) can be passed
to the ``shortener`` function too:

::

    import shorten

    # Use an alternative alphabet with faces
    alphabet = [
      ':)', ':(', ';)', ';(', '>:)', ':D', ':x', ':X', ':|', ':O', '><', '<<', '>>', '^^', 'O_o', u'?_?',
    ]

    shortener = shorten.shortener('memory', alphabet=alphabet)

    values = [
      'aardvark', 
      'bonobo', 
      'caiman', 
      'degu', 
      'elk',
    ]

    keys = map(shortener.insert, values)

    # [':(:):):)', ':(:):):(', ':(:):);)', ':(:):);(', ':(:):)>:)']
    print(keys)

For a working example, see ``example.py``.
""",
   **kw
)     
