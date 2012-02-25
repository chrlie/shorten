__all__ = ['MemoryKeystore']

class MemoryKeystore(object):
   def __init__(self, keygen=None):
      self._data = {}
      self._keygen = keygen

   def insert(self, obj):
      """
      Insert an object into the keystore and returns the key used.
      """
      key = self._keygen.next()
      if key in self._data:
         raise KeyError('key has been used')
 
      self._data[key] = obj
      return key

   def __getitem__(self, key):
      return self._data[key]

   def __iter__(self):
      return iter(self._data)

   def __len__(self):
      return len(self._data)

   def set_keygen(self, keygen):
      if self._keygen is None:
         self._keygen = iter(keygen)
      else:
         raise ValueError('keygen has already been set')

   def get_keygen(self):
      return self._keygen

   # The class used to generate keys
   keygen = property(get_keygen, set_keygen)
