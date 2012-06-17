import keygens
import keystores

__version__ = '0.2.1'
__all__ = ['keygens', 'shortener', 'keystores', '__version__', 'shorteners']

shorteners = ('memory', 'mongo', 'redis', 'redis-bucket', 'sqlalchemy')

def shortener(name, min_length=4, start=None, alphabet=None, **kwargs):
  """
  Simplifies creation of keystores.
  
    'redis'     creates a redis-backed keystore
    'memory'    creates a memory-backed keystore
  """

  if name == 'memory':      
    keygen = keygens.MemoryKeygen(min_length=min_length, 
                                  start=start, 
                                  alphabet=alphabet)   
    return keystores.MemoryKeystore(keygen, **kwargs)      
  elif name == 'mongo':
    raise NotImplemented()    
  elif name == 'redis':   
    counter_key = kwargs.pop('counter_key', None)
    redis = kwargs['redis']      
    keygen = keygens.RedisKeygen(min_length=min_length, 
                                 start=start, 
                                 alphabet=alphabet, 
                                 counter_key=counter_key, 
                                 redis=redis)
    return keystores.RedisKeystore(keygen, **kwargs)
  elif name == 'redis-bucket':
    raise NotImplemented()
  elif name == 'sqlalchemy':
    raise NotImplemented()      
  else:
    raise Exception("valid shorteners are %s" % ', '.join(shorteners))
