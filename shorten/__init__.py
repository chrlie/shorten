import key
import token
import store

from store import BaseStore, MemoryStore, MemoryKeygen, RedisStore, RedisKeygen, MemcacheStore, MemcacheKeygen
from token import TokenGenerator, UUIDTokenGenerator 
from formatter import Formatter
from errors import KeyInsertError, TokenInsertError, RevokeError

__version__ = '2.0.0'

stores = ('memcache', 'memory', 'redis')

def make_store(name, min_length=4, **kwargs):
   """\
   Creates a store with a reasonable keygen.

   * memory - data and keys are created and stored in memory. Keys are allocated and
              returned in increasing order.

   * redis  - data and keys are created and stored in Redis. Some keys may be missed,
              but are allocated in increasing order.

   * redis-bucket - keys may be returned in a random order. Both data and keys are
                    created and stored in Redis.
   *
   ::
   * hey
   * you


   .. admonition:: A note on security

      Once someone figures out your alphabet, they can make a reasonable guess
      that you're encoding numbers sequentially.

      Take a URL shortener service with a 'private posting' option. A determined
      user can guess an alphabet and enumerate every key after their own.
      
      If that's your concern, use UUIDs or buckets.

   .. admonition:: A note on buckets

      Buckets are intended to prevent casual enumeration of keys by making the
      keyspace sparser. Don't rely on this for any sort of security, because
      it doesn't offer any.

      If that's your concern, use random UUIDs.

   :param formatter:       hey

   Test

   :param min_length:       the minimum key length, in characters.
   :param start:            the starting index that the keygen counts from.
 
   :param alphabet:         the alphabet to use. Any indexable object
                            can be used as an alphabet.

   :param formatter:        an object used to format the internal key
                            and token names. :class:`Formatter <Formatter>`
                            provides a default implementation, returning the key
                            and token unmodified.

   :param token_gen:        An object used to generate revokation tokens.
                            :class:`TokenGenerator <shorten.token.TokenGenerator>` 
                            provides a default implementation, which returns the 
                            key as the revokation token.
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

