__all__ = ['Formatter', 'NamespacedFormatter', 'FormatterMixin']

class Formatter(object):  
   """\
   A formatter is used to format the internal representation of a key or token. 
   This is useful for Redis and SQL databases, which often need to prefix keys
   and columns in order to avoid clashes.

   .. admonition:: Subclassing

      Subclasses should implement ``format_key(key)`` and 
      ``format_token(token)``. 

   """

   def format_key(self, key):
      """\
      Formats a key.
      """
      return key

   def format_token(self, token):
      """\
      Formats a token.
      """
      return token

class FormatterMixin(object):
   def format_key(self, key):
      return self.formatter.format_key(key)

   def format_token(self, token):
      return self.formatter.format_token(token)

   def format_pair(self, pair):
      fkey = self.formatter.format_key(pair.key)
      ftoken = self.formatter.format_token(pair.token)
      return (fkey, ftoken)

class NamespacedFormatter(object):
   """\
   Prefixes keys and tokens with `namespace` string.

   :param namespace:    a string to prefix to keys and tokens.
   """

   separator = ':'

   def __init__(self, namespace):
      self.ns = namespace      

   def format_key(self, key):
      return '{ns}{s}keys{s}{key}'.format(ns=self.ns,
         s=self.separator, key=key)

   def format_token(self, token):
       return '{ns}{s}tokens{s}{token}'.format(ns=self.ns,
         s=self.separator, token=token)
  
