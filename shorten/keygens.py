__all__ = ['SequentialKeygen']

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

class SequentialKeygen(object):
   def __init__(self, min_length=4, alphabet=None):     
      self._alphabet = alphabet or DEFAULT_ALPHABET      

      if min_length <= 0:
         min_length = 0

      self._start = len(self._alphabet) ** (min_length-1)

   def __iter__(self):
      return self.key_generator(self._start)

   def key_generator(self, start, total=None):
      c = start

      # Loop manually because xrange overflows with large numbers
      while True:
         if total is not None and c >= start + total:
            break

         yield bx_encode(c, self._alphabet)
         c += 1
