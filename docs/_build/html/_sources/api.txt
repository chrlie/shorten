API 
---

This part of the documentation covers the developer interfaces of Shorten.

Base Classes
~~~~~~~~~~~~

The base class used to create and operate stores. Methods that should be 
implemented by a custom class are indicated.

.. autoclass:: shorten.BaseStore
   :members:

The base class for key generators. 

.. autoclass:: shorten.BaseKeyGenerator
   :members:

Memory Stores
~~~~~~~~~~~~~

.. autoclass:: shorten.MemoryStore
   :members:

.. autoclass:: shorten.MemoryKeygen
   :members:

Redis Stores
~~~~~~~~~~~~

.. autoclass:: shorten.RedisStore
   :members:

.. autoclass:: shorten.RedisKeygen
   :members:

Memcache Stores
~~~~~~~~~~~~~~~

.. autoclass:: shorten.MemcacheStore
   :members:

.. autoclass:: shorten.MemcacheKeygen
   :members:

Token Generators
~~~~~~~~~~~~~~~~

.. autoclass:: shorten.TokenGenerator
   :members:

.. autoclass:: shorten.UUIDTokenGenerator
   :members:
