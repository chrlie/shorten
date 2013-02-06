import key
import token
import store

from formatter import Formatter

__version__ = '1.0.1'
__all__ = ['__version__', 'key', 'token', 'store', 'make_store', 'stores', 'Formatter']

stores = ('memcache', 'memory', 'mongo', 'redis', 'redis-bucket', 'sqlalchemy')

def make_store(name, **kwargs):
  """\
  Simplifies creation of stores by linking them with the appropriate keygens.
  
  Valid stores names are:

     `redis`       A redis-backed store.

     `memory`      A memory-backed store.

  Keyword arguments are:

     `min_length`       The minimum key length, in characters.

     `start`            The starting index that the keygen counts from.

     `alphabet`         The alphabet to use: any indexable object
                        can be used as an alphabet.

     `formatter`        An object used to format the internal key
                        and token names. ``Formatter`` provides a
                        default implementation, returning the key
                        and token unmodified.

     `token_generator`  An object used to generate revokation tokens.
                        ``token.TokenGenerator`` provides a default
                        implementatio, which returns the key as the
                        revokation token.
  """
  
  keygen_args = {
   'min_length': kwargs.pop('min_length', 4),
   'start': kwargs.pop('start', None),
   'alphabet': kwargs.pop('alphabet', None),
  }

  store_args = kwargs

  if name == 'memcache':
    raise NotImplementedError()

  elif name == 'memory':      
    keygen = key.MemoryKeygen(**keygen_args)
    return store.MemoryStore(keygen, **store_args)      

  elif name == 'mongo':
    raise NotImplementedError()    

  elif name == 'redis':   
    keygen_args.update({
      'redis_counter_key': kwargs.pop('redis_counter_key', None),
      'redis': kwargs.get('redis', None),
    })

    keygen = key.RedisKeygen(**keygen_args)
    return store.RedisStore(keygen, **store_args)

  elif name == 'redis-bucket':
    raise NotImplementedError()

  elif name == 'sqlalchemy':
    raise NotImplementedError()      

  else:
    e = Exception("valid stores are %s" % ', '.join(stores))
    raise e

