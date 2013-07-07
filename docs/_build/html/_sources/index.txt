.. shorten documentation master file, created by
   sphinx-quickstart on Mon Jun 10 19:35:28 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


===================

Shorten is a `MIT licensed <http://opensource.org/licenses/MIT>`_ library for storing your data 
with auto-generated short keys. Use an in-memory, Redis or memcache backend with Shorten.

I made this library after being unable to find a satsifactory URL shortening
library. Shorten increments a counter but without clever tricks and obfiscuated
schemes that produce unmaintainable code.

Replace this:

::

   import random

   ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456790-_'
   BASE = len(ALPHABET)
   ALPHABET = random.shuffle(ALPHABET)

   def encode(n):
      digits = []

      while n > 0:
         digits.append(ALPHABET[n % BASE])
         n = n // BASE

      return ''.join(digits)


User Guide
----------

.. toctree::
   :maxdepth: 2

   user/intro
   user/advanced
   user/examples

API Documentation
-----------------

.. toctree::
   :maxdepth: 2

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

