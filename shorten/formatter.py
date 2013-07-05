class Formatter(object):  
   """\
   A :class:`Formatter <Formatter>` returns modified copies of keys and tokens
   suitable for internal storage in a store. ::

      class PrefixedFormatter(object):
         def format_key(self, key):
            return 'some-prefix-{key}'.format(key)

         def format_token(self, token):
            return token.encode(self.encoding)

   When implementing your own store, you can use :meth:`formatter.format_key`
   and :meth:`formatter.format_token` to transform keys and tokens.
   """

   def format_key(self, key):
      return key

   def format_token(self, token):
      return token

class FormatterMixin(object):
   """\
   Provides 
   """      

   def format_key(self, key):
      return self.formatter.format_key(key)

   def format_token(self, token):
      return self.formatter.format_token(token)

   def format_pair(self, pair):
      fkey = self.formatter.format_key(pair.key)
      ftoken = self.formatter.format_token(pair.token)
      return (fkey, ftoken)
