import keygens
import keystores

__version__ = '0.2.0'
__all__ = ['keygens', 'shortener', 'keystores', '__version__']

def shortener(name, min_length=4, start=None, total=None, alphabet=None, **kwargs):
   """
   Simplifies creation of keystores.

      'redis'     creates a redis-backed keystore
      'memory'    creates a memory-backed keystore
   """

   if name == 'redis':   
      counter_key = kwargs.pop('counter_key', None)
      keygen = keygens.RedisKeygen(min_length=min_length, 
                                   start=start, 
                                   total=total, 
                                   alphabet=alphabet, 
                                   counter_key=counter_key, 
                                   redis=kwargs['redis'])
      return keystores.RedisKeystore(keygen, **kwargs)
      
   elif name == 'memory':      
      keygen = keygens.MemoryKeygen(min_length=min_length, 
                                    start=start, 
                                    total=total, 
                                    alphabet=alphabet)   
      return keystores.MemoryKeystore(keygen, **kwargs)
      
   else:
      raise Exception("valid shorteners are 'redis' or 'memory'")
