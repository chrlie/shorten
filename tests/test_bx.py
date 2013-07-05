import nose

from shorten.key import bx_encode, bx_decode

def test_bx_encode_wrong_type():
   alphabet = 'abc'
   string = 'a'
   nose.tools.assert_raises(TypeError, lambda: bx_encode(string, alphabet))  

def test_bx_decode_empty():
   alphabet = ''
   string = 'a string'
   nose.tools.assert_raises(ValueError, lambda: bx_decode(string, alphabet))

   alphabet = 'abc'
   string = ''
   nose.tools.assert_raises(ValueError, lambda: bx_decode(string, alphabet))

def test_bx_encode_decode_mapping():
   alphabet = 'abc'
   mapping = {'a': 0, 'b': 1, 'c': 2}
   
   encoded = bx_encode(3, alphabet)
   assert encoded == 'ba'

   decoded = bx_decode(encoded, alphabet, mapping)
   assert decoded == 3

   decoded = bx_decode('ba', alphabet, mapping)
   assert decoded == 3

def test_bx_encode_decode_deadbeef():
   alphabet = '0123456789abcdef'
   
   deadbeef = bx_encode(0xdeadbeef, alphabet)   
   assert deadbeef == 'deadbeef'

   deadbeef = bx_decode(deadbeef, alphabet)
   assert deadbeef == 0xdeadbeef

