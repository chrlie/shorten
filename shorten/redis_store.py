# Needed to import from the PyRedis package
from __future__ import absolute_import

from redis import WatchError

from .base import BaseStore, Pair

from .key import BaseKeyGenerator
from .formatter import FormatterMixin
from .errors import KeyInsertError, TokenInsertError

class RedisKeygen(BaseKeyGenerator):
   """\
   Creates keys in Redis. Keys are always generated in increasing order.

   :param redis:           an open Redis connection.
   :param counter_key:     the Redis key in which to store the keygen's
                           counter value.
   """
  
   def __init__(self, redis_client=None, counter_key=None, **kwargs):
      super(RedisKeygen, self).__init__(**kwargs)

      if counter_key is None:
         raise ValueError('a counter key is required')

      if redis_client is None:
         raise ValueError('a Redis client is required')

      self.counter_key = counter_key
      self.redis = redis_client

   def __iter__(self):
      """\
      Increments the Redis counter and yields a new key.
      """
    
      ckey = self.counter_key
      start = self.start
  
      while True:           
         i = self.redis.incr(ckey) + start - 1      
         yield self.encode(i)

class RedisStore(BaseStore, FormatterMixin):
   """\
   Stores keys, tokens and data in Redis.   

   If `key_gen` is `None`, a :class:`RedisKeygen <shorten.RedisKeygen` 
   will be created with the following paramters:

   =================  ===================================================
   `alphabet`         an iterable of characters in an alphabet.      
   `min_length`       the minimum key length to begin generating keys at.

   `start`            the number to start the keygen's counter at.

   `counter_key`      the Redis key in which to store the keygen's
                      counter value.

   `redis_client`     an open Redis connection.
   =================  ===================================================

   :param counter_key:     the Redis key in which to store the keygen's
                           counter value.
   :param key_gen:         a key generator. If `None`, a new key
                           generator is created (see above).

   :param redis_client:    an open Redis connection.
   :type key_gen:          a RedisKeyGen or None
   """
  
   def __init__(self, **kwargs):
      redis_client = kwargs.pop('redis_client', None)
      counter_key = kwargs.pop('counter_key', None)
   
      # Get all the arguments for the keygen
      alphabet = kwargs.pop('alphabet', None)
      min_length = kwargs.pop('min_length', None)
      start = kwargs.pop('start', None)
      key_gen = kwargs.get('key_gen', None)

      if redis_client is None:
         raise ValueError('a Redis client is required')

      # Create a reasonable keygen if it isn't provided
      if key_gen is None:
         key_gen = RedisKeygen(redis_client=redis_client, alphabet=alphabet, 
               counter_key=counter_key, min_length=min_length, start=start)

      super(RedisStore, self).__init__(key_gen=key_gen, **kwargs)

      self.redis = redis_client
      self.counter_key = counter_key

   def insert(self, val, pipe=None):
      """\
      Inserts a value and returns a :class:`Pair <shorten.Pair>`.

      .. admonition :: Key Safety

         Keys and tokens are always inserted with a :class:`Pipeline`, so 
         irrevocable keys will never occur.
      
      If `pipe` is given, :class:`KeyInsertError <shorten.KeyInsertError>` and 
      :class:`TokenInsertError <shorten.TokenInsertError>` will not be thrown 
      if duplicate keys and tokens exist. Instead, the nth-from-last results 
      must be checked:
      
      ::
      
         pipe = redis.pipeline()
         key, token = short.insert('value', pipe)
         results = pipe.execute()
         
         if not results[-2]:
            raise KeyInsertError(key)

         if not results[-1]:
            raise TokenInsertError(token)


      :attr val:     a value to insert.
      :attr pipe:    a Redis pipeline. If `None`, the pair will
                     be returned immediately. Otherwise they must be
                     extracted from the pipeline results (see above).
      """
     
      p = self.redis.pipeline() if pipe is None else pipe
      
      try:
         key, token, formatted_key, formatted_token = self.next_formatted_pair()

         p.watch(formatted_key, formatted_token)

         # Make this atomic
         p.multi()      

         # Associate both the value and token with the key to
         # allow `get_token(key)`
         p.hsetnx(formatted_key, 'value', val)
         p.hsetnx(formatted_key, 'token', token)
         p.setnx(formatted_token, key)
         
         if pipe is None:
            results = p.execute()

            if not results[-2] or not results[-3]:
               raise KeyInsertError(key, 'key exists')

            if not results[-1]:
               raise TokenInsertError(token, 'token exists')

         return Pair(key, token)

      except WatchError:
         raise

      finally:
         if pipe is None:
            p.reset()                  
 
   def revoke(self, token, pipe=None):
      """\
      Revokes the key associated with the given revokation token.

      If the token does not exist, a :class:`KeyError <KeyError>` is thrown. 
      Otherwise `None` is returned.

      If `pipe` is given, then a :class:`RevokeError <shorten.RevokeError>` 
      will not be thrown if the key does not exist. The n-th from last result
      should be checked like so:

      ::

         pipe = redis.Pipeline()
         store.revoke(token, pipe=pipe)
        
         results = pipe.execute()
         if not results[-1]:
            raise RevokeError(token)
         

      :param pipe:   a Redis pipeline. If `None`, the token will
                     be revoked immediately. Otherwise they must be
                     extracted from the pipeline results (see above).
      """
      
      p = self.redis.pipeline() if pipe is None else pipe    
      
      formatted_token = self.format_token(token)

      try:         
         p.watch(formatted_token)

         # Get the key immediately
         key = p.get(formatted_token)
         formatted_key = self.format_key(key)

         # Make this atomic
         p.multi()
         p.delete(formatted_key, formatted_token)
        
         if pipe is None:
            if not p.execute()[-1]:
               raise RevokeError(token, 'token not found')         

      except WatchError:
         raise

      finally:
         if pipe is None:
            p.reset()

   def get_value(self, key):
      key = self.format_key(key)
      value = self.redis.hget(key, 'value')

      if value is None:
         raise KeyError(key)
      else:
         return value

   def has_key(self, key):
      key = self.format_key(key)
      return self.redis.exists(key)
      
   def has_token(self, token):
      token = self.format_token(token)
      return self.redis.exists(token)

   def get_token(self, key):
      key = self.format_key(key)
      return self.redis.hget(key, 'token')

