import uuid

__all__ = ['TokenGenerator', 'UUIDTokenGenerator']

class TokenGenerator(object):
   def create_token(self, key):
      return key

class UUIDTokenGenerator(TokenGenerator):
   def create_token(self, key):
      return str(uuid.uuid4())
