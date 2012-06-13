__all__ = ['MemoryKeystore', 'RedisKeystore']

def default_formatter(key):
   return key

class Keystore(object):
   def peek(self):
      return self._formatter(self._keygen.peek())

class MemoryKeystore(Keystore):
   def __init__(self, keygen, formatter=None, incrementer=None):
      self._data = {}
      self._keygen = keygen
      self._formatter = formatter or default_formatter

   def insert(self, data=None):
      key = self._formatter(self._keygen.next())
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

class RedisKeystore(Keystore):
   def __init__(self, keygen, redis, formatter=None):
      self._redis = redis
      self._keygen = keygen
      self._formatter = formatter or default_formatter

   def insert(self, val, after_insert=None, before_insert=None): 
      # This atomically increments the counter. It's assumed to not matter
      # if everything after this fails and a number is unallocated
      # This will also overwrite existing keys
      key = self._formatter(self._keygen.next())
      pipe = self._redis.pipeline()
      if before_insert is not None:
        before_insert(pipe)                
      pipe.setnx(key, val)
      if after_insert is not None:
        after_insert(pipe, key)
      pipe.execute()
      return key

   def __setitem__(self, key, val):
      return self._redis.set(key, val)
      
   def __getitem__(self, key):
      ret = self._redis.get(key)
      if ret is None:
         raise KeyError(key)
      return ret

   def __iter__(self):
      return NotImplemented()
   
   def __len__(self):
      return NotImplemented()
