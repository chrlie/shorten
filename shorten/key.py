"""\
The basics of key generation.

:data DEFAULT_ALPHABET:       contains the numbers 0-9 and letters a-Z
:data DISSIMILAR_ALPHABET:    excludes similar characters 0, O, 1, l, I
                              (zero, uppercase 'o', one, lowercase 'l'
                              and uppercase 'i')
"""

from collections import Mapping, Iterable

__all__ = ['bx_encode', 'bx_decode', 'Keygen', 'DEFAULT_ALPHABET', 'DISSIMILAR_ALPHABET']

DEFAULT_ALPHABET = '1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
DISSIMILAR_ALPHABET = '23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def bx_encode(n, alphabet):
   """\
   Encodes an integer `n` in base `len(alphabet)` with digits in `alphabet`.
 
   ::

      # 'ba'
      bx_encode(3, 'abc')

   :param n:            a positive integer
   :param alphabet:     a 0-based iterable
   """
 
   if not isinstance(n, int):
      raise TypeError('an integer is required')

   base = len(alphabet)

   if n == 0:
      return alphabet[0]

   digits = []
   
   while n > 0:
      digits.append(alphabet[n % base])
      n = n // base
   
   digits.reverse()
   return ''.join(digits)

def bx_decode(string, alphabet, mapping=None):
   """\
   Transforms a string in `alphabet` to an integer.
   
   If `mapping` is provided, each key must map to its positional
   value without duplicates.

   ::

      mapping = {'a': 0, 'b': 1, 'c': 2}

      # 3
      bx_decode('ba', 'abc', mapping)
   
   :param string:       a string consisting of key from `alphabet`
   :param alphabet:     a 0-based iterable
   
   :param mapping:      a :class:`Mapping`. If `None`, the inverse
                        of `alphabet` is used, with values mapped
                        to indices.
   """
  
   mapping = mapping or dict([(d, i) for (i, d) in enumerate(alphabet)])
   base = len(alphabet)

   if not string:
      raise ValueError('string cannot be empty')

   if not isinstance(mapping, Mapping):
      raise TypeError('a Mapping is required')

   sum = 0

   for digit in string:
      try:
         sum = base*sum + mapping[digit]
      except KeyError:
         raise ValueError(
            "invalid literal for bx_decode with base %i: '%s'" % (base, digit))

   return sum

class BaseKeyGenerator(Iterable):
   """\
   An iterator that converts a base-10 number to a string in a given alphabet.
   Leading zero-characters are not included.

   :param start:        the number to start iteration at.
   :param min_length:   the length of the string to start iteration at. Leading
                        zero-characters are not counted in the length.

   ::

      # Using hex
      k = Keygen(min_length=3, alphabet='0123456789abcdef')

      # ['100', '101', '102', '103', '104']
      [key for key in islice(k, 0, 5)]

   Only one of `start` or `min_length` should be given.
   """
  
   def __init__(self, alphabet=None, min_length=None, start=None):           
      min_length = max(0, min_length)
      alphabet = alphabet or DEFAULT_ALPHABET   

      if start is None:
         start = len(alphabet) ** (min_length-1)      

      # Raise an error if there are duplicates
      seen = set()
      for sym in alphabet:
         if sym in seen:
            raise ValueError("alphabet contains duplicate symbol '{0}'".format(sym))
         seen.add(sym)

      self.alphabet = alphabet
      self.start = start

   def encode(self, n):
      return bx_encode(n, self.alphabet)

