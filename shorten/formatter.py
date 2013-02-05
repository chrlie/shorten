__all__ = ['Formatter']

class Formatter(object):  
   """\
   A formatter modifies the key (or revokation token) before it is stored
   in a Keystore. Externally visible keys (and revokation tokens) are not
   altered by the formatter.
   """

   def format_token(self, token):
      return token

   def format_key(self, key):
      return key
