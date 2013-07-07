from .base import BaseStore, Pair

from .key import BaseKeyGenerator
from .lock import Lock
from .formatter import FormatterMixin
from .errors import KeyInsertError, TokenInsertError, RevokeError

class MemoryKeygen(BaseKeyGenerator):
   """\
   Creates keys in-memory. Keys are always generated in increasing order.
   """
 
   def __iter__(self):
      """\
      Increments the in-memory counter and yields a new key.      
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
   Stores keys, tokens and data in memory.

   If `key_gen` is `None`, a :class:`MemoryKeygen <shorten.MemoryKeygen>`
   will be created with the following paramters:

   =================  ===================================================
   `alphabet`         an iterable of characters in an alphabet.      
   `min_length`       the minimum key length to begin generating keys at.

   `start`            the number to start the keygen's counter at.
   =================  ===================================================

   :param key_gen:    a key generator. If `None`, a new key
                      generator is created (see above).

   :type key_gen:     a MemoryKeygen or None
   """
  
   def __init__(self, **kwargs):
      alphabet = kwargs.pop('alphabet', None)
      min_length = kwargs.pop('min_length', None)
      start = kwargs.pop('start', None)      
      key_gen = kwargs.get('key_gen', None)

      # Provide a reasonable default keygen
      if key_gen is None:
         key_gen = MemoryKeygen(alphabet=alphabet, min_length=min_length, 
            start=start)

      super(MemoryStore, self).__init__(key_gen=key_gen, **kwargs)

      self._data = {}
      self._tokens = {}  

   def insert(self, val):     
      key, token, formatted_key, formatted_token = self.next_formatted_pair()

      # To be consistent, the `has_key` and `has_token` methods are used
      if self.has_key(key):
         raise KeyInsertError(key, 'key exists')

      if self.has_token(token):
         raise TokenInsertError(token, 'token exists')

      self._data[formatted_key] = (val, token)
      self._tokens[formatted_token] = key

      return Pair(key, token)

   def revoke(self, token):
      formatted_token = self.format_token(token)

      try:
         key = self._tokens[formatted_token]
      except KeyError:
         raise RevokeError(token, 'token not found')
        
      formatted_key = self.format_key(key)

      del self._data[formatted_key]
      del self._tokens[formatted_token]

   def get_value(self, key):
      key = self.format_key(key)
      return self._data[key][0]

   def has_key(self, key):
      return self.format_key(key) in self._data
      
   def has_token(self, token):      
      return self.format_token(token) in self._tokens

   def get_token(self, key):
      key = self.format_key(key)
      return self._data[key][1]

   def __iter__(self):
      """\
      Iterates over all keys.
      """
      return iter(self._data)

   def __len__(self):
      """\
      The number of keys in the store.
      """
      return len(self._data)       
