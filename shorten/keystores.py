import collections
import operator
import itertools

try:
  import gevent.coros
  __gevent__ = True
except ImportError:
  __gevent__ = False
  
__all__ = ['MemoryKeystore', 'RedisKeystore', 'default_formatter']

def default_formatter(key):
  return key

class Keystore(object):
  def __init__(self, keygen, formatter=None):
    self._keygen = keygen
    self._formatter = formatter or default_formatter

  def _next(self, *args, **kwargs):
    format = self._formatter
    next = self._keygen.next(*args, **kwargs)    
    return [format(t) for t in iter(next)]

  keygen = property(lambda self: self._keygen)
  formatter = property(lambda self: self._formatter)

class MemoryKeystore(Keystore):
  """\
  Stores formatted short keys and their values in memory.
  """
  
  def __init__(self, *args, **kwargs):
    super(MemoryKeystore, self).__init__(*args, **kwargs)
    self._data = {}
    self._revokation = {}
    
    if __gevent__:
      self._lock = gevent.coros.Semaphore()
    else:
      self._lock = None      

  def _acquire(self):
    if self._lock is not None:
      self._lock.acquire()  
  
  def _release(self):
    if self._lock is not None:
      self._lock.release()  

  def insert_multi(self, *vals):
    """\
    Insert multiple values efficiently. Returns an iterator of keys, even if
    only one value was provided.
    """    
    
    length = len(vals)
    keys = self._next(length)
    kv = itertools.izip(keys, vals)
    
    for key, val in kv:
      self._data[key] = val
      
    return iter(keys)

  def insert(self, val):
    """\
    Generates a new short key, inserts the value into memory and returns the key.
    """
        
    key = self._next()[0]
    self._data[key] = val
    return key

  def insert_with_revoke(self, val, revoke_key):
    self._acquire()
    
    if revoke_key in self._revokation:
      raise KeyError('Revokation key exists.')
      
    short_key = self.insert(val)
    self._revokation[revoke_key] = short_key
    
    self._release()
    
    return short_key

  def revoke(self, revoke_key):
    """\
    Revokes (deletes) the short key associated with the given revokation key `revoke_key`.
    If `revoke_key` does not exist, throws a KeyError. Otherwise returns True.
    """

    try:
      short_key = self._revokation[revoke_key]
    except KeyError:
      raise KeyError('Revokation key does not exist.')

    del self._data[short_key]
    del self._revokation[revoke_key]
    return True

  def __setitem__(self, key, item):
    self._data[key] = item

  def __getitem__(self, key):
    return self._data[key]

  def __iter__(self):
    return iter(self._data)

  def __len__(self):
    return len(self._data)
 
class RedisKeystore(Keystore):
  """\
  Stores formatted short keys and their values in Redis.
  """
  
  def __init__(self, keygen, redis, **kwargs):
    super(RedisKeystore, self).__init__(keygen, **kwargs)
    self._redis = redis

  def insert_multi(self, *vals):
    """\
    Insert multiple values efficiently. Returns an iterator of keys, even if
    only one value was provided.
    """    
    
    length = len(vals)    
    keys = self._next(length)
    p = self._redis.pipeline()    
    
    for key, val in zip(keys, vals): 
      p.set(key, val)
      
    p.execute()
    return iter(keys)
    
  def insert(self, val, pipe=None): 
    """\
    Generates a new short key, inserts a value into Redis and returns the key.
        
    If ``pipe`` is given, the values is inserted on calling ``pipe.execute``.
    Otherwise, the value is immediately insert and the key returned.
       
    Keys are *always* generated, so orphaned keys may occur if the pipeline
    is broken before a value can be inserted.
    """

    p = self._redis.pipeline() if pipe is None else pipe
    key = self._next()[0]
    p.set(key, val)
  
    # Execute immediately if there was no user-supplied pipe  
    if pipe is None:    
      p.execute()
    return key 
 
  def insert_with_revoke(self, val, revoke_key, pipe=None):
    """\
    Generates a new short key and a revokation key, which can be used
    to delete the short key and value.
    
    If ``pipe`` is given, this function cannot check for an existing
    revokation key. This can be accomplished by checking the nth-from-last 
    result:
    
      pipe = redis.pipeline()
      key = short.insert_with_revoke('value', 'revoke-key', pipe)
      results = pipe.execute()
      
      if results[-1] == 0:
        raise KeyError('Revokation key already exists.')    
    """
    
    p = self._redis.pipeline() if pipe is None else pipe
    
    try:
      short_key = self.insert(val, pipe=p)
      p.setnx(revoke_key, short_key)
      
      if pipe is None:
        if p.execute()[0] == 0:
          raise KeyError('Revokation key exists.')
      return short_key
    finally:
      if pipe is None:
        p.reset()            
 
  def revoke(self, revoke_key, pipe=None):
    """\
    Revokes (deletes) the short key associated with the given revokation key `revoke_key`.
    If `revoke_key` does not exist, throws a KeyError. Otherwise returns True.  

    If a Redis pipeline is given, no value is returned.
    """
    
    p = self._redis.pipeline() if pipe is None else pipe   
    
    try:      
      p.watch(revoke_key)
      short_key = p.get(revoke_key)
      p.multi()
      p.delete(short_key, revoke_key)
      
      if pipe is None:
        if p.execute()[-1] == 0:
          raise KeyError('Revokation key does not exist.')
        else:
          return True
    except redis.WatchError:
      raise
    finally:
      if pipe is None:
        p.reset()
 
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
