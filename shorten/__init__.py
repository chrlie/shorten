import key
import token
import store

from formatter import Formatter

__version__ = '1.0.0'
__all__ = ['__version__', 'key', 'token', 'store', 'make_store', 'stores', 'Formatter']

stores = ('memcache', 'memory', 'mongo', 'redis', 'redis-bucket', 'sqlalchemy')

def make_store(name, **kwargs):
  """\
  Simplifies creation of stores by linking them with the appropriate keygens.
  
  Valid stores are:

    'redis'     A redis-backed store.
    'memory'    A memory-backed store.

  `min_length`  The minimum key length, in characters.

  `start`       The index to start counting from.

  `alphabet`    The alphabet to use: any indexable object
                can be used as an alphabet.

  """
  
  keygen_args = {
   'min_length': kwargs.pop('min_length', 4),
   'start': kwargs.pop('start', None),
   'alphabet': kwargs.pop('alphabet', None),
  }

  store_args = kwargs

  if name == 'memcache':
    raise NotImplemented()

  elif name == 'memory':      
    keygen = key.MemoryKeygen(**keygen_args)
    return store.MemoryStore(keygen, **store_args)      

  elif name == 'mongo':
    raise NotImplemented()    

  elif name == 'redis':   
    keygen_args.update({
      'redis_counter_key': kwargs.pop('redis_counter_key', None),
      'redis': kwargs.get('redis', None),
    })

    keygen = key.RedisKeygen(**keygen_args)
    return store.RedisStore(keygen, **store_args)

  elif name == 'redis-bucket':
    raise NotImplemented()

  elif name == 'sqlalchemy':
    raise NotImplemented()      

  else:
    raise Exception("valid stores are %s" % ', '.join(stores))

