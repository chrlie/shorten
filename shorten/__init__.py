import alphabets
import key
import store
import token

from errors import KeyInsertError, TokenInsertError, RevokeError
from formatter import Formatter, NamespacedFormatter
from key import BaseKeyGenerator
from store import BaseStore, MemoryStore, MemoryKeygen, RedisStore, RedisKeygen, MemcacheStore, MemcacheKeygen
from token import TokenGenerator, UUIDTokenGenerator 

__version__ = '2.0.0'

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

