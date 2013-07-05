from .base import BaseStore, Pair

from ..lock import Lock
from ..key import BaseKeyGenerator
from ..formatter import FormatterMixin
from ..errors import KeyInsertError, TokenInsertError

class MemcacheKeygen(BaseKeyGenerator):
   """\
   Generates keys in memcache.
   """
 
   def __init__(self, memcache_client=None, counter_key=None, **kwargs):
      super(MemcacheKeygen, self).__init__(**kwargs)

      if counter_key is None:
         raise ValueError('a counter key is required')

      self.counter_key = counter_key
      self._mc = memcache_client

   def __iter__(self):
      ckey = self.counter_key
      start = self.start
      mc = self._mc
     
      # Create a start value 
      lock = Lock()
      lock.acquire()

      # Create a start value if it doesn't exist
      current = mc.get(ckey)
      if current is None:
         mc.set(ckey, 0)

      lock.release()

      while True:
         i = int(mc.incr(ckey)) + start - 1
         yield self.encode(i)

class MemcacheStore(BaseStore, FormatterMixin):
   """\
   Stores formatted short keys and their values in memory.
   """
 
   def __init__(self, **kwargs):
      memcache_client = kwargs.pop('memcache_client', None)
      counter_key = kwargs.pop('counter_key', None)    
      alphabet = kwargs.pop('alphabet', None)
      min_length = kwargs.pop('min_length', None)
      start = kwargs.pop('start', None)
      key_gen = kwargs.get('key_gen', None)

      # Create a reasonable keygen if it isn't provided
      if key_gen is None:
         key_gen = MemcacheKeygen(
               memcache_client=memcache_client, alphabet=alphabet, counter_key=counter_key, 
               min_length=min_length, start=start)
         kwargs['key_gen'] = key_gen

      if memcache_client is None:
         raise ValueError('a memcache client is required')

      super(MemcacheStore, self).__init__(**kwargs)
      self._mc = memcache_client

   def insert(self, val):     
      """\
      Insert a val and return a :class:`Pair <Pair>`, which
      is a :class:`tuple`. It contains a key and token (in
      that order) as well `key` and `token` attributes.
      
      ::

         pair = store.insert('aardvark')
         key, token = pair

         # True
         pair.key == pair[0] == key

         # True
         pair.token == pair[1] == token

      If the generated key exists or memcache cannot store it, a 
      :class:`KeyInsertError <KeyInsertError>` is raised (or a
      :class:`TokenInsertError <TokenInsertError>` if a token
      exists or cannot be stored).      
      """

      key, token, formatted_key, formatted_token = self.next_formatted_pair()

      if self.has_key(key):
         raise KeyInsertError(key)

      if self.has_token(token):
         raise TokenInsertError(token)

      # Memcache is down or read-only

      if not self._mc.add(formatted_key, val):
         raise KeyInsertError(key, 'key could not be stored')

      if not self._mc.add(formatted_token, key):
         raise TokenInsertError(token, 'token could not be stored')

      return Pair(key, token)

   def revoke(self, token):
      formatted_token = self.format_token(token)

      try:
         key = self._mc.get(formatted_token)
      except KeyError:
         raise RevokeError('revokation token not found')
        
      formatted_key = self.format_key(key)

      del self._mc[formatted_key]
      del self._mc[formatted_token]

   def get_value(self, key):
      key = self.format_key(key)
      val = self._mc.get(key)

      if val is None:
         raise KeyError(key)

      return val

   def has_key(self, key):
      key = self.format_key(key)
      return self._mc.get(key) is not None
      
   def has_token(self, token):      
      token = self.format_token(token)
      return self._mc.get(token) is not None
