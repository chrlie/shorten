from .keygens import SequentialKeygen
from .keystores import MemoryKeystore

class Shortener(object):
   """
   Maps objects to short keys.
   """

   def __init__(self, keystore=None, keygen=None, min_length=4):
      self._keystore = keystore or MemoryKeystore()
      self._keygen = keygen or SequentialKeygen(min_length)
      self._keystore.keygen = self._keygen

   def insert(self, obj):
      return self._keystore.insert(obj)

   def __getitem__(self, key):
      return self._keystore[key]

   def __len__(self):
      return len(self._keystore)
