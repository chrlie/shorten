import operator

try:
  import gevent.coros
  __gevent__ = True
except ImportError:
  __gevent__ = False

__all__ = ['Keygen', 'MemoryKeygen', 'RedisKeygen']

DEFAULT_ALPHABET = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def bx_encode(n, alphabet):
  """\
  Encodes an integer ``n`` as a string by mapping it to the 0-indexed iterable ``alphabet``.
  """
  
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
  """\
  Decodes ``string`` with the 0-indexed iterable ``alphabet``, or if ``mapping`` is
  provided, use that to lookup the digit for a symbol.
  """
  
  mapping = mapping or dict([(d, i) for (i, d) in enumerate(alphabet)])
  b = len(alphabet)

  try:
    return sum([b**i * mapping[d] for (i,d) in enumerate(reversed(string))])
  except KeyError as e:
    raise ValueError("invalid literal for bx_decode with base %i: '%s'" % (b, string))

def largerange(start, stop, step=1):
  """\
  A replacement for xrange.
  xrange throws OverFlow errors with numbers that don't fit in a C long.
  """
  if step < 0:
    comp = operator.gt
  else:
    comp = operator.lt   
  
  c = start
  
  while comp(c, stop):
    yield c
    c += step

class Keygen(object):
  """\
  Generates keys with symbols from an ``alphabet``. 
  The keys may or may not be in lexographic order.``min_length`` or ``start`` can
  be specified to generate keys of a certain string length or larger.
  """
  
  def __init__(self, alphabet=None, min_length=4, start=None):
    self._alphabet = alphabet or DEFAULT_ALPHABET
    
    if min_length is not None and start is not None:
      raise Exception("only one of 'min_length' or 'start' can be set")

    min_length = max(0, min_length)

    if start is None:
      self._start = len(self._alphabet) ** (min_length-1)
    else:
      self._start = start

  def next(self):
    raise NotImplemented()

  def map(self, n):
    return bx_encode(n, self._alphabet)

  alphabet = property(lambda self: self._alphabet)
  start = property(lambda self: self._start)

class MemoryKeygen(Keygen):
  """\
  Generates keys in-memory.
  """
  
  def __init__(self, *args, **kwargs):
    super(MemoryKeygen, self).__init__(*args, **kwargs)
    self._current = self._start  
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

  def _next_generator(self, start, total):  
    for i in largerange(start, total):
      yield self.map(i)

  def next(self, num=1):
    """\
    Increments the in-memory counter immediately and returns a new key.
    """
    self._acquire()
    current = self._current
    self._current += num
    
    if num == 1:
      self._release()
      return [self.map(current)]
    else:
      self._release()    
      return self._next_generator(current, current+num)      

class RedisKeygen(Keygen):
  """\
  Generates keys in-memory but increments them in Redis.
  """
  
  DEFAULT_COUNTER_KEY = 'shorten:counter'
  
  def __init__(self, *args, **kwargs):
    self._counter_key = kwargs.pop('counter_key', self.DEFAULT_COUNTER_KEY)
    self._redis = kwargs.pop('redis')
    super(RedisKeygen, self).__init__(*args, **kwargs)

  def next(self, num=1):
    """\
    Increments the global Redis counter immediately and returns a new key.
    """
    
    ckey = self._counter_key
    start = self._start
    redis = self._redis
    
    if num == 1:
      return [self.map(redis.incr(ckey) + start - 1)]
    else:
      with redis.pipeline() as pipe:
        for i in largerange(0, num):
          pipe.incr(ckey)
        return [self.map(token + start - 1) for token in pipe.execute()]
    
  counter_key = property(lambda self: self._counter_key)
