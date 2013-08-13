.. _install:

Installation
------------

Install with pip:

.. code:: sh

   $ pip install shorten

Shorten uses `redis-py <https://github.com/andymccurdy/redis-py>`_ as its
Redis client and it will be downloaded automatically. This dependency may 
be removed in a future version.

If you want to run the tests, install the requirements in ``requirements.txt``:

.. code:: sh

   $ virtualenv --no-site-packages .python && source .python/bin/activate
   $ pip install -r requirements.txt

A Redis server and Memcached server are required for testing. The 
``memcached`` and ``libevent`` (for `gevent`) development libraries are 
also required. For Debian-based systems, install everything by:

.. code:: sh
   
   $ apt-get install python-dev libmemcached-dev libevent-dev redis memcached

