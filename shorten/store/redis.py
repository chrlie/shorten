# Needed to import from the PyRedis package
from __future__ import absolute_import

from redis import WatchError

from .base import BaseStore, Pair

from ..key import BaseKeyGenerator
from ..formatter import FormatterMixin
from ..errors import KeyInsertError, TokenInsertError

class RedisKeygen(BaseKeyGenerator):
   """\
   Generates keys in-memory but increments them in Redis.   

   :param redis:           an open Redis connection.
   :param counter_key:     the Redis key for the keygen's counter
   """
  
   def __init__(self, redis_client=None, counter_key=None, **kwargs):
      super(RedisKeygen, self).__init__(**kwargs)

      if counter_key is None:
         raise ValueError('a counter key is required')

      if redis_client is None:
         raise ValueError('a Redis connection is required')

      self.counter_key = counter_key
      self.redis = redis_client

   def __iter__(self):
      """\
      Increments the global Redis counter immediately and returns a new key.
      """
    
      ckey = self.counter_key
      start = self.start
  
      while True:           
         i = self.redis.incr(ckey) + start - 1      
         yield self.encode(i)

class RedisStore(BaseStore, FormatterMixin):
   """\
   Stores values in Redis.
   
   :param redis:     a Redis connection.

   :meth:`insert` takes an optional :class:`redis.Pipeline <pipeline>` 
  
   Multiple insertions or revokations can be performed with :meth:`bulk`,
   which will put all insertions and revokations in a pipeline before
   executing them. 

   ::

      try:
         with store.bulk() as bulk:
            bulk.insert('aardvark')
            bulk.insert('bonobo')
            bulk.insert('caiman')

      except BulkError as e:         
         pass
   """
   
   def __init__(self, **kwargs):
      redis_client = kwargs.pop('redis_client', None)
      counter_key = kwargs.pop('counter_key', None)
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
         kwargs['key_gen'] = key_gen

      super(RedisStore, self).__init__(**kwargs)
      self._redis = redis_client

   def insert(self, val, pipe=None):
      """\
      Creates and returns a key and revokation token, inserts the value
      with that key, and returns the tuple (key, revokation token).

      Keys are *always* generated, so orphaned keys may occur if the pipeline
      is broken before a value can be inserted.
      
      If :attr:`pipe` is given, this function cannot check for an existing
      keys or tokens. This can be accomplished by checking the nth-from-last 
      results 
      
      ::
      
         pipe = redis.pipeline()
         key, token = short.insert('value', pipe)
         results = pipe.execute()
         
         if not results[-2]:
            raise KeyInsertError(key)

         if not results[-1]:
            raise TokenInsertError(token)
      """
      
      p = self._redis.pipeline() if pipe is None else pipe
      
      try:
         key, token, formatted_key, formatted_token = self.next_formatted_pair()

         p.setnx(formatted_key, val)
         p.setnx(formatted_token, key)
         
         if pipe is None:
            results = p.execute()

            if not results[-2]:
               raise KeyInsertError(key)

            if not results[-1]:
               raise TokenInsertError(token)

         return Pair(key, token)

      finally:
         if pipe is None:
            p.reset()                  
 
   def revoke(self, token, pipe=None):
      """\
      Revokes (deletes) the key associated with the given revokation token.
      If the token does not exist, throws a KeyError. Otherwise returns True.   

      :param pipe:   a Redis :class:`Pipeline`. If not `None`, no value
                     will be returned.
      """
      
      p = self._redis.pipeline() if pipe is None else pipe    
      
      formatted_token = self.format_token(token)

      try:         
         p.watch(formatted_token)

         key = p.get(formatted_token)
         formatted_key = self.format_key(key)

         p.multi()
         p.delete(formatted_key, formatted_token)
         
         if pipe is None:
            if p.execute()[-1] == 0:
               raise RevokeError("revokation token '{0}' not found".format(token))
            else:
               return True

      except WatchError:
         raise

      finally:
         if pipe is None:
            p.reset()

   def get_value(self, key):
      key = self.format_key(key)
      value = self._redis.get(key)

      if value is None:
         raise KeyError(key)
      else:
         return value

   def has_key(self, key):
      key = self.format_key(key)
      return self._redis.get(key) is not None
      
   def has_token(self, token):
      token = self.format_token(token)
      return self._redis.get(token) is not None

