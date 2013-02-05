import operator
from lock import Lock

__all__ = ['Keygen', 'MemoryKeygen', 'RedisKeygen']

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
  Generates keys with symbols from an indexable ``alphabet``. 
  The keys may or may not be in lexographic order.``min_length`` or ``start`` can
  be specified to generate keys of a certain string length or larger.
  """

  DEFAULT_ALPHABET = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
  
  def __init__(self, alphabet=None, min_length=4, start=None):    
    self._alphabet = alphabet or self.DEFAULT_ALPHABET
    
    if min_length is not None and start is not None:
      raise Exception("only one of 'min_length' or 'start' can be set")

    min_length = max(0, min_length)

    if start is None:
      self._start = len(self._alphabet) ** (min_length-1)
    else:
      self._start = start

  def encode(self, n):
    return bx_encode(n, self._alphabet)

  alphabet = property(lambda self: self._alphabet)
  start = property(lambda self: self._start)

class MemoryKeygen(Keygen):
  """\
  Generates keys in-memory.
  """
 
  def __iter__(self):
    """\
    Increments the in-memory counter immediately and returns a new key.
    """

    lock = Lock()
    current = self._start

    while True:
      try:
        lock.acquire()    
        yield self.encode(current)
        current += 1

      finally:
        lock.release()

class RedisKeygen(Keygen):
  """\
  Generates keys in-memory but increments them in Redis.
  """
  
  COUNTER_KEY = 'counter'
  
  def __init__(self, *args, **kwargs):
    self._counter_key = kwargs.pop('redis_counter_key', self.COUNTER_KEY)
    self._redis = kwargs.pop('redis', None)

    if self._redis is None:
      raise Exception('A Redis object is required for the RedisKeygen.')

    super(RedisKeygen, self).__init__(*args, **kwargs)

  def __iter__(self):
    """\
    Increments the global Redis counter immediately and returns a new key.
    """
    
    ckey = self.counter_key
    start = self._start
   
    while True:           
      i = self._redis.incr(ckey) + start - 1      
      yield self.encode(i)
    
  @property
  def counter_key(self):
    return self._counter_key
