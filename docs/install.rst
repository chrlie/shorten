.. _install:

Installation
------------

Install with pip:

.. code:: sh

   $ pip install shorten

If you want to run the tests, install the requirements in ``requirements.txt``:

.. code:: sh

   $ virtualenv --no-site-packages .python && source .python/bin/activate
   $ pip install -r requirements.txt

A Redis server, memcache server and the ``memcached`` development libraries are 
also required. Redis, memcache and gevent tests can be skipped by passing
``redis``, ``gevent`` or ``memcache`` to nose:

.. code:: sh

   $ nosetests tests -v -a !redis,!gevent,!memcache

