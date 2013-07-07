from ..formatter import Formatter
from ..token import TokenGenerator

class NamedTuple(object):
   """\
   Make our own version of namedtuple that isn't so ugly.

   :param name:   the name of the class. 
   
   If the class name is not given, all attributes are 
   capitalized and concatenated to 'NamedTuple' as the 
   class name. ::

      HelloWorldNamedTuple = NamedTuple('hello', 'world')

      # 'HelloWorldNamedTuple'
      HelloWorldNamedTuple.__name__

   """

   def __new__(cls, *attrs, **kwargs):
      cls_name = '{0}NamedTuple'.format(''.join([a.capitalize() for a in attrs]))
      new_name = kwargs.get('name', cls_name)

      def __new__(cls, *args):
         return tuple.__new__(cls, args)

      def __getnewargs__(self):
         return tuple(self)

      def __repr__(self):
         args = ['{0}={1}'.format(attr, repr(self[i])) for (i, attr) in enumerate(attrs)]
         pairs = ', '.join(args)
         return '{name}({pairs})'.format(name=self.__class__.__name__, pairs=pairs)

      new_attrs = {
         '__new__': __new__,
         '__getnewargs__': __getnewargs__,
         '__repr__': __repr__,
      }

      def make_attr(i):
         return lambda self: tuple.__getitem__(self, i)

      # Create an attribute with the names
      for i, attr in enumerate(attrs):
         new_attrs[attr] = property(make_attr(i))

      return type(new_name, (tuple,), new_attrs)

class Pair(NamedTuple('key', 'token')):
   """\
   A named tuple that contains a key and token.
   """

   pass

class FormattedPair(NamedTuple('key', 'token', 'formatted_key', 'formatted_token')):
   """\
   The same as Pair, but also containing the formatted key and token.
   """

   pass

class BaseStore(object):
   """\
   A key-value store that has auto-generated keys. Deletion is through
   `tokens`, which are generated along with keys. A `key` cannot be
   used to delete a value (unless they are the same value).
   
   ::

      s = Store()
      key, token = s.insert('aardvark')

      # 'aardvark'
      s[key]
      
      # Removes 'aardvark'      
      del s[token]

      # None
      s.get(key, None)


   Because they are closely associated, keys and tokens are returned 
   in a :class:`Pair <Pair>`. A :class:`Pair <Pair>` is a named :class:`tuple`
   containing a `key` and `token` (in that order) as well `key` and `token` 
   attributes.

   ::

      s = Store()
      pair = s.insert('aardvark')

      # 'aardvark'
      s[pair.key]

      # Removes 'aardvark'
      del s[pair.token]

      pair = store.insert('bonobo')
      key, token = pair

      # True
      pair.key == pair[0] == key

      # True
      pair.token == pair[1] == token


   Unlike a Python :class:`dict`, a :class:`BaseStore <BaseStore>` allows 
   insertion but no modification of its values. Some stores may provide 
   :meth:`__len__`  and :meth:`__iter__` methods if the underlying storage 
   mechanism makes it feasible.

   :param key_gen:        a :class:`Keygen` that generates unique keys.

   :param formatter:      a :class:`Formatter` used to transform keys and
                          tokens for storage in a backend.

   :param token_gen:      an object with a :meth:`create_token` method
                          that returns unique revokation tokens.            
   """

   def __init__(self, key_gen=None, formatter=None, token_gen=None):
      formatter = formatter or Formatter()
      token_gen = token_gen or TokenGenerator()
      key_gen = iter(key_gen)

      self.key_gen = key_gen   
      self.token_gen = token_gen
      self.formatter = formatter

   def __contains__(self, key):
      return self.has_key(key)

   def __getitem__(self, key):
      return self.get_value(key)

   def __delitem__(self, token):
      return self.revoke(token)

   def next_formatted_pair(self):
      """\
      Returns a :class:`FormattedPair <FormattedPair>` containing attributes 
      `key`, `token`, `formatted_key` and `formatted_token`. Calling this method 
      will always consume a key and token.
      """

      key = self.key_gen.next()
      token = self.token_gen.create_token(key)
      fkey = self.formatter.format_key(key)
      ftoken = self.formatter.format_token(token)

      return FormattedPair(key, token, fkey, ftoken)

   def get(self, key, default=None):
      """\
      Get the value for :attr:`key` or :attr:`default` if the
      key does not exist.
      """

      try:
         return self[key]
      except KeyError:
         return default

   # Methods that should be implemented if you create your own class. 

   def insert(self, val):      
      """\
      Insert a val and return a :class:`Pair <Pair>`, which
      is a :class:`tuple`. It contains a key and token (in
      that order) as well `key` and `token` attributes.
      
      ::

         pair = store.insert('aardvark')
         key, token = pair

         # True
         pair.key == pair[0] == key

         # True
         pair.token == pair[1] == token


      If the generated key exists or the cannot be stored, a
      :class:`KeyInsertError` is raised (or a :class:`TokenInsertError`
      for tokens).

      ::

         try:
            store.insert('bonobo')
         except (KeyInsertError, TokenInsertError):
            print('Cannot insert')
            
      """

      raise NotImplementedError

   def revoke(self, token):
      """\
      Revokes the :attr:`token`. A :class:`RevokeError <RevokeError>` is 
      raised if the token is not found or the underlying storage
      cannot complete the revokation.

      ::
      
         try:
            store.revoke(token)
            print('Revoked!')
         except RevokeError:
            print('Could not revoke')

      """

      raise NotImplementedError

   def get_value(self, key):
      """\
      Gets the value for :attr:`key` or raise a :class:`KeyError <KeyError>`
      if it doesn't exist.
      :meth:`get` and `store[key]` will call this method.
      """

      raise NotImplementedError

   def has_key(self, key):            
      raise NotImplementedError

   def has_token(self, token):
      raise NotImplementedError
