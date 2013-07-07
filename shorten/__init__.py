#from __future__ import absolute_import

#rom . import alphabets
#rom . import key
#rom . import token
#rom . import errors
#rom . import formatter

from .base import BaseStore, Pair
from .memory_store import MemoryStore, MemoryKeygen
from .redis_store import RedisStore, RedisKeygen
from .memcache_store import MemcacheStore, MemcacheKeygen

from .errors import KeyInsertError, TokenInsertError, RevokeError
from .formatter import Formatter, NamespacedFormatter
from .key import BaseKeyGenerator
from .token import TokenGenerator, UUIDTokenGenerator 

from .version import __version__

stores = ('memcache', 'memory', 'redis')

def make_store(name, min_length=4, **kwargs):
   """\
   Creates a store with a reasonable keygen.

   .. deprecated:: 2.0.0
      Instantiate stores directly e.g. ``shorten.MemoryStore(min_length=4)``

   """
  
   if name not in stores:
      raise ValueError('valid stores are {0}'.format(', '.join(stores)))

   if name == 'memcache':
      store = MemcacheStore
   elif name == 'memory':
      store = MemoryStore
   elif name == 'redis':
      store = RedisStore

   return store(min_length=min_length, **kwargs)

