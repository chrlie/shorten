__all__ = ['Keygen', 'incrementer']

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

def incrementer(start, total=None):
   if __gevent__:
      lock = gevent.coros.Semaphore()
   else:
      lock = None

   c = start

   # Loop manually because xrange overflows with large numbers
   while True:
      if lock is not None:
         lock.acquire()

      if total is not None and c >= start + total:
         break
      val = c
      c += 1

      if lock is not None:
         lock.release()

      yield val

class Keygen(object):
   def __init__(self, min_length=4, alphabet=None, start=None, total=None):     
      self._alphabet = alphabet or DEFAULT_ALPHABET      

      if min_length <= 0:
         min_length = 0

      if min_length is not None and start is not None:
         raise Exception("only one of 'min_length' or 'start' can be set")

      if start is None:
         self._start = len(self._alphabet) ** (min_length-1)
      else:
         self._start = start

      self._total = total

   def __iter__(self):
      return self.key_generator()

   def key_generator(self, key_incrementer=None):
      key_incrementer = key_incrementer or incrementer
      for key in key_incrementer(self._start, self._total):
         yield bx_encode(key, self._alphabet)

   def get_start(self):
      return self._start

   def get_total(self):
      return self._total

   start = property(get_start)
   total = property(get_total)
