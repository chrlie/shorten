__all__ = ['MemoryKeystore', 'RedisKeystore']

try:
   import gevent.coros
   __gevent__ = True
except ImportError:
   __gevent__ = False

def default_formatter(key):
   return key

class MemoryKeystore(object):
   def __init__(self, keygen, formatter=None):
      self._data = {}
      self._keygen = keygen.key_generator()
      self._formatter = formatter or default_formatter

   def insert(self, data=None):
      """
      Insert an object into the keystore and returns the key used.
      """
      key = self._formatter(self._keygen.next())
      if key in self._data:
         raise KeyError('key has been assigned')
 
      self._data[key] = data
      return key

   def __setitem__(self, key, item):
      self._data[key] = item

   def __getitem__(self, key):
      return self._data[key]

   def __iter__(self):
      return iter(self._data)

   def __len__(self):
      return len(self._data)

class RedisKeystore(object):

   DEFAULT_COUNTER_KEY = 'shorten:counter'

   def __init__(self, keygen, connection, counter_key=None, formatter=None):
      self._redis = connection
      self._keygen = keygen.key_generator(self._incrementer)
      self._counter_key = counter_key or self.DEFAULT_COUNTER_KEY
      self._formatter = formatter or default_formatter

   def _incrementer(self, start, total=None):
      while True:         
         val = self._redis.incr(self._counter_key) + start - 1
         yield val

   def clear_counter(self):
      self._redis.delete(self._counter_key)

   def insert(self, data=None):
      # We're okay to increment and set in two atomic steps, since
      # the counter is never decremented   
      key = self._formatter(self._keygen.next())
      if not self._redis.setnx(key, data):
         raise KeyError('key has been assigned')
      return key

   def __setitem__(self, key, val):
      self._redis.set(key, val)
      
   def __getitem__(self, key):
      ret = self._redis.get(key)
      if ret is None:
         raise KeyError(key)
      return ret

   def get_redis(self):
      return self._redis

   def set_redis(self, v):
      self._redis = v

   property(get_redis, set_redis)      
