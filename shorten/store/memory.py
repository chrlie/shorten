from .base import BaseStore, Pair

from ..key import BaseKeyGenerator
from ..lock import Lock
from ..formatter import FormatterMixin
from ..errors import KeyInsertError, TokenInsertError, RevokeError

class MemoryKeygen(BaseKeyGenerator):
   """\
   Generates keys in-memory.
   """
 
   def __iter__(self):
      """\
      Increments the in-memory counter immediately and returns a new key.
      """

      lock = Lock()
      current = self.start

      while True:
         try:
            lock.acquire()    
            yield self.encode(current)
            current += 1

         finally:
            lock.release()

class MemoryStore(BaseStore, FormatterMixin):
   """\
   Stores formatted short keys and their values in memory.
   """
  
   def __init__(self, **kwargs):
      alphabet = kwargs.pop('alphabet', None)
      min_length = kwargs.pop('min_length', None)
      start = kwargs.pop('start', None)      
      key_gen = kwargs.get('key_gen', None)

      if key_gen is None:
         key_gen = MemoryKeygen(alphabet=alphabet, min_length=min_length, start=start)
         kwargs['key_gen'] = key_gen

      super(MemoryStore, self).__init__(**kwargs)

      self._data = {}
      self._tokens = {}  

   def insert(self, val):     
      key, token, formatted_key, formatted_token = self.next_formatted_pair()

      # To be consistent, the `has_key` and `has_token` methods are used
      if self.has_key(key):
         raise KeyInsertError(key)

      if self.has_token(token):
         raise TokenInsertError(token)

      self._data[formatted_key] = val
      self._tokens[formatted_token] = key

      # A `Pair` is a tuple, so this is consistent with versions < 2
      return Pair(key, token)

   def revoke(self, token):
      formatted_token = self.format_token(token)

      try:
         key = self._tokens[formatted_token]
      except KeyError:
         raise RevokeError('revokation token not found')
        
      formatted_key = self.format_key(key)

      del self._data[formatted_key]
      del self._tokens[formatted_token]

   def get_value(self, key):
      key = self.format_key(key)
      return self._data[key]

   def has_key(self, key):
      return self.format_key(key) in self._data
      
   def has_token(self, token):      
      return self.format_token(token) in self._tokens

   def __iter__(self):
      return iter(self._data)

   def __len__(self):
      return len(self._data)       

