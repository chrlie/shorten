API 
---

This part of the documentation covers the developer interfaces of Shorten.

Store Objects
~~~~~~~~~~~~~

The base classes used to create and operate stores. Methods that should be 
implemented by a custom class are indicated.

.. autoclass:: shorten.BaseStore
   :members:

.. autoclass:: shorten.BaseKeyGenerator
   :members:

.. autofunction:: shorten.make_store

Memory Stores
~~~~~~~~~~~~~

.. autoclass:: shorten.MemoryStore
   :members:
   :inherited-members:

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

Formatter Objects
~~~~~~~~~~~~~~~~~

.. autoclass:: shorten.Formatter
   :members:

.. autoclass:: shorten.NamespacedFormatter
   :members:

Encoding and Decoding
~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: shorten.key.bx_encode
.. autofunction:: shorten.key.bx_decode
