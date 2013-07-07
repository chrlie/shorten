import uuid

__all__ = ['TokenGenerator', 'UUIDTokenGenerator']

class TokenGenerator(object):
   """\
   A token generator which returns the key passed to it.
   """

   def create_token(self, key):
      return key

class UUIDTokenGenerator(TokenGenerator):
   """\
   A token generator which returns a UUID4 (random) token.
   See https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_.28random.29
   """

   def create_token(self, key):
      return str(uuid.uuid4())
