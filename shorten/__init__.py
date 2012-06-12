import keygens
import keystores

__version__ = 0.1
__all__ = ['keygens', 'shortener', 'keystores', '__version__']

def shortener(name, min_length=4, **kwargs):
   """
   Simplifies creation of keystores.

      'redis'     creates a redis-backed keystore
      'memory'    creates a memory-backed keystore
   """

   keygen = keygens.Keygen(min_length=min_length)

   if name == 'redis':         
      return keystores.RedisKeystore(keygen, **kwargs)
   elif name == 'memory':
      return keystores.MemoryKeystore(keygen, **kwargs)
   else:
      raise Exception("valid shorteners are 'redis' or 'memory'")
