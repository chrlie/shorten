__all__ = ['Keygen', 'MemoryKeygen', 'RedisKeygen']

try:
   import gevent.coros
   __gevent__ = True
except ImportError:
   __gevent__ = False

DEFAULT_ALPHABET = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def bx_encode(n, alphabet):
   b = len(alphabet)

   if n == 0:
      return alphabet[0]
   else:
      digits = []
      while n > 0:
         digits.append(alphabet[n % b])
         n = n // b
      digits.reverse()
      return ''.join(digits)

def bx_decode(string, alphabet, mapping=None):
   mapping = mapping or dict([(d, i) for (i, d) in enumerate(alphabet)])
   b = len(alphabet)

   try:
      return sum([b**i * mapping[d] for (i,d) in enumerate(reversed(string))])
   except KeyError, e:
      raise ValueError("invalid literal for bx_decode with base %i: '%s'" % (b, string))

class Keygen(object):
   """\
   Generates keys.
   """

   def __init__(self, alphabet=None, min_length=4, start=None, total=None):
      self._alphabet = alphabet or DEFAULT_ALPHABET
      self._total = total     
      
      if min_length is not None and start is not None:
         raise Exception("only one of 'min_length' or 'start' can be set")

      min_length = max(0, min_length)

      if start is None:
         self._start = len(self._alphabet) ** (min_length-1)
      else:
         self._start = start

   def map(self, n):
      return bx_encode(n, self._alphabet)

   alphabet = property(lambda self: self._alphabet)
   start = property(lambda self: self._start)

class MemoryKeygen(Keygen):
  """\
  Generates keys in-memory. Gevent-safe, but not threadsafe.
  """
  def __init__(self, *args, **kwargs):
    super(MemoryKeygen, self).__init__(*args, **kwargs)
    self._current = self._start   
    if __gevent__:
      self._lock = gevent.coros.Semaphore()
    else:
      self._lock = None                            

  def peek(self):    
    return self.map(self._current)

  def next(self):
    if self._lock is not None:
      self._lock.acquire()
  
    if self._total is not None and c >= self._start + self._total:
      raise StopIteration()
    val = self._current
    self._current += 1

    if self._lock is not None:
      self._lock.release()

    return self.map(val)

class RedisKeygen(Keygen):
  """\
  Generates keys in-memory but increments them in redis. Gevent-safe but
  not threadsafe.
  """
  
  DEFAULT_COUNTER_KEY = 'shorten:counter'
  
  def __init__(self, *args, **kwargs):
    self._counter_key = kwargs.pop('counter_key', self.DEFAULT_COUNTER_KEY)
    self._redis = kwargs.pop('redis')    
    super(RedisKeygen, self).__init__(*args, **kwargs)
  
  def peek(self, pipe=None):    
    pipe = pipe or self._redis
    return self.map(pipe.get(self._counter_key))

  def next(self, pipe=None):      
    pipe = pipe or self._redis
    return self.map(pipe.incr(self._counter_key) + self._start - 1)
