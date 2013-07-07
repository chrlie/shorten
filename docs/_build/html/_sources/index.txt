.. shorten documentation master file, created by
   sphinx-quickstart on Mon Jun 10 19:35:28 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Shorten
=======

Release v\ |version|. (:ref:`Installation <install>`)

Shorten is a `MIT licensed <http://opensource.org/licenses/MIT>`_ Python library
for storing your data with automatically generated keys. Use your choice of
backend: in-memory, Redis and Memcached are supported by default.

I made this library after being unable to find anything satisfactory for
URL shortening. Shorten contains no clever tricks or obfuscated schemes 
that produce unmaintainable code.

It's gevent-safe, so you can use it with Gunicorn and Heroku (and
consequently Flask, Django, Pyramid). Currently, it is neither
threadsafe nor multiprocess safe.

User Guide
----------

.. toctree::
   :maxdepth: 2

   install
   user/intro
   user/examples

API Documentation
-----------------

.. toctree::
   :maxdepth: 2

   api

Indices and tables
------------------

* :ref:`genindex`

