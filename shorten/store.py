import collections
import operator
import itertools
import weakref

try:
   import redis
   from redis.exceptions import WatchError
except ImportError:
   pass

from formatter import Formatter
from token import TokenGenerator
from lock import Lock

__all__ = ['MemoryStore', 'RedisStore', 'RedisBucketStore', 'MemoryBucketStore']

class Store(object):
   """\
   Stores keys, tokens and values.
   """

   def __init__(self, keygen, formatter=None, token_generator=None):
      self._keyiter = iter(keygen)
      self._formatter = formatter or Formatter()
      self._tokengen = token_generator or TokenGenerator()

   def next_key_token_pair(self, num=1):
      """\
      Returns an iterator of ``num`` key/revokation token tuples if num > 1,
      otherwise returns a single tuple.
      """

      if num == 1:
         key = self._keyiter.next()
         token = self.tokengen.create_token(key)
         return key, token
      else:
         result = lambda key: (key, self.tokengen.create_token(key))
         return itertools.imap(result, self._keyiter)
 
   def insert(self, val):
      pass

   def revoke(self, token):
      pass

   def get(self, key, default=None):
      try:
         return self[key]
      except KeyError:
         return default

   def has_key(self, key):
      pass

   def has_token(self, token):
      pass

   keygen = property(lambda self: self._keygen)
   formatter = property(lambda self: self._formatter)
   tokengen = property(lambda self: self._tokengen)
 
class Bucket(object):
   def __init__(self, capacity, max_capacity):
      pass

   def __len__(self):      
      """\
      The current number of keys in the bucket.
      """
      return self._count

   def get_capacity(self):
      """\
      The total number of keys that can be added to this bucket.
      Not necessarily the same as the bucket's ``max_capacity``.
      """
      return self._capacity

   def get_remaining(self):
      """\
      The remaining number of keys that can be added to this bucket.
      """
      return self.capacity - len(self)

   def get_max_capacity(self):
      return self._max_capacity

   max_capacity = property(get_max_capacity)
   capacity = property(get_capacity)
   remaining = property(get_remaining)      

class BucketStore(object):
   """\   
   Instead of sequentially generating keys, keys are selected from
   a fixed-size bucket   
   """

   def __init__(self, bucket_size):
      pass

   def create_bucket(self):
      pass

class MemoryStore(Store):
   """\
   Stores formatted short keys and their values in memory.
   """
  
   class Bulk(object):
      def __init__(self, keystore):
         self._keystore = weakref.proxy(keystore)

      def __enter__(self):
         self._keystore._lock.acquire()
         return self

      def __exit__(self, *args, **kwargs):
         self._keystore._lock.release()

      def insert(self, val):
         return self._keystore._insert(val)         

      def revoke(self, token):
         return self._keystore._revoke(token)
 
   def __init__(self, *args, **kwargs):
      super(MemoryStore, self).__init__(*args, **kwargs)

      self._lock = Lock()
      self._data = {}
      self._tokens = {}  

   def has_token(self, token):
      formatted_token = self.formatter.format_token(token)
      return formatted_token in self._tokens

   def _insert(self, val):     
      key, token = self.next_key_token_pair(1)

      if self.has_token(token):
         raise KeyError("Revokation token '{0}' exists.".format(token))

      formatted_key = self.formatter.format_key(key)
      formatted_token = self.formatter.format_token(token)

      self._data[formatted_key] = val
      self._tokens[formatted_token] = key

      return key, token

   def _revoke(self, token):
      formatted_token = self.formatter.format_token(token)
      key = self._tokens[formatted_token]
      formatted_key = self.formatter.format_key(key)

      del self._data[formatted_key]
      del self._tokens[formatted_token]

      return True

   def bulk(self):
      return self.Bulk(self)

   def insert(self, val):
      """\
      Generates a new key, inserts the value into memory and returns a tuple
      of (key, revokation token).
      """

      try:
         self._lock.acquire()
         return self._insert(val)         

      finally:
         self._lock.release()

   def revoke(self, token):
      """\
      Revokes (deletes) the key and value associated with the given revokation token.
      If ``token`` does not exist, a KeyError is thrown.
      """

      try:
         self._lock.acquire()
         return self._revoke(token)         
        
      except KeyError:
         raise KeyError("Revokation token '{0}' does not exist.".format(token))

      finally:
         self._lock.release()

   def has_key(self, key):
      return key in self
      
   def has_token(self, token):      
      formatted_token = self.formatter.format_token(token)
      return formatted_token in self._tokens
 
   def __contains__(self, key):
      formatted_key = self.formatter.format_key(key)
      return formatted_key in self._data

   def __iter__(self):
      return iter(self._data)

   def __len__(self):
      return len(self._data) 
      
   def __getitem__(self, key):      
      formatted_key = self.formatter.format_key(key)

      return self._data[formatted_key]

   def __iter__(self):
      return iter(self._data)

   def __len__(self):
      return len(self._data)
 
class RedisStore(Store):
   """\
   Stores formatted short keys and their values in Redis.
   """
   
   class Bulk(object):
      def __init__(self, keystore):
         self._keystore = weakref.proxy(keystore)

      def __enter__(self):         
         self._pipeline = self._keystore._redis.pipeline()
         return self

      def __exit__(self, *args, **kwargs):
         self._pipeline.execute()       

      def insert(self, val):
         return self._keystore.insert(val, pipe=self._pipeline)

      def revoke(self, token):
         return self._keystore.revoke(token, pipe=self._pipeline)

      @property
      def pipeline(self):
         return self._pipeline

   def __init__(self, *args, **kwargs):
      self._redis = kwargs.pop('redis', None)                

      if self._redis is None:
         raise Exception('A Redis object is required for the RedisStore')

      super(RedisStore, self).__init__(*args, **kwargs)

   def bulk(self):
      return self.Bulk(self)

   def insert(self, val, pipe=None):
      """\
      Creates and returns a key and revokation token, inserts the value
      with that key, and returns the tuple (key, revokation token).

      Keys are *always* generated, so orphaned keys may occur if the pipeline
      is broken before a value can be inserted.
      
      If ``pipe`` is given, this function cannot check for an existing
      revokation key. This can be accomplished by checking the nth-from-last 
      result:
      
         pipe = redis.pipeline()
         key = short.insert('value', pipe)
         results = pipe.execute()
         
         if results[-1] == 0:
            raise KeyError('Revokation key already exists.')      
      """
      
      p = self._redis.pipeline() if pipe is None else pipe
      
      try:
         key, token = self.next_key_token_pair()
         formatted_key = self.formatter.format_key(key)
         formatted_token = self.formatter.format_token(token)

         p.set(formatted_key, val)
         p.setnx(formatted_token, key)
         
         if pipe is None:
            if p.execute()[0] == 0:
               raise KeyError("Revokation token '{0}' exists.".format(token))

         return key, token

      finally:
         if pipe is None:
            p.reset()                  
 
   def revoke(self, token, pipe=None):
      """\
      Revokes (deletes) the key associated with the given revokation token.
      If the token does not exist, throws a KeyError. Otherwise returns True.   

      If a Redis pipeline is given, no value is returned.
      """
      
      p = self._redis.pipeline() if pipe is None else pipe    
      
      formatted_token = self.formatter.format_token(token)

      try:         
         p.watch(formatted_token)

         key = p.get(formatted_token)
         formatted_key = self.formatter.format_key(key)

         p.multi()
         p.delete(formatted_key, formatted_token)
         
         if pipe is None:
            if p.execute()[-1] == 0:
               raise KeyError("Revokation token '{0}' does not exist.".format(token))
            else:
               return True

      except WatchError:
         raise

      finally:
         if pipe is None:
            p.reset()

   def has_key(self, key):
      return key in self
      
   def has_token(self, token):
      formatted_token = self.formatter.format_token(token)
      return self._redis.get(formatted_token) is not None
 
   def __contains__(self, key):
      formatted_key = self.formatter.format_key(key)
      return self._redis.get(formatted_key) is not None

   def __iter__(self):
      raise NotImplemented()

   def __len__(self):
      raise NotImplemented()
      
   def __getitem__(self, key):      
      formatted_key = self.formatter.format_key(key)
      ret = self._redis.get(formatted_key)

      if ret is None:
         raise KeyError(key)

      return ret

