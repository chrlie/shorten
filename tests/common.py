import sys
import functools
from types import MethodType

import gevent
import nose

import shorten
from shorten.lock import Lock
from shorten import UUIDTokenGenerator, KeyInsertError, TokenInsertError, RevokeError

def spawn_nicely(*args):
   g = gevent.spawn(*args)
   g.link_exception(die_nicely)   
   return g

def die_nicely(*args):   
#   msg = 'greenlet died: {0}'.format(','.join(args))
   msg = 'greenlet died'
   gevent.hub.get_hub().parent.throw(SystemExit(msg))

# Reuse the same key and token
def wrap_next_formatted_pair(store, key, token):   
   FormattedPair = shorten.base.FormattedPair
   
   @functools.wraps(store.next_formatted_pair)
   def mock(self):
      formatted_key = self.formatter.format_key(key)
      formatted_token = self.formatter.format_token(token)

      return FormattedPair(key, token, formatted_key, formatted_token)

   store.next_formatted_pair = MethodType(mock, store)
  
class TokenGen(object):
   def create_token(self, key):
      return key

class BaseKeyGenTest(object):
   pass

class LenTestMixin(object):
   pass

class IterTestMixin(object):
   pass

class GeventTestMixin(object):
   """\
   A mixin for running insertion and revokation tests using gevent.
   """

   def test_gevent_insert_many(self):
      n = self.many_num
      baseline_store = self.get_baseline()
      store = self.get_store()
      values = self.make_some_values(n)

      def insert(val):
         baseline_key, baseline_token = baseline_store.insert(val)
         key, token = store.insert(val)

         assert baseline_key == key
         assert baseline_token == token
         assert key in store
         assert store.has_token(token)
         assert store.has_key(key)
         assert store[key] == val              
      
         baseline_triple = (baseline_key, baseline_token, val)
         triple = (key, token, val)

         return (baseline_triple, triple)

      jobs = []

      for val in values:
         jobs.append(spawn_nicely(insert, val))

      gevent.joinall(jobs)      
      
      baseline = set()
      test = set()

      for job in jobs:
         baseline_triple, triple = job.value
         baseline.add(baseline_triple)
         test.add(triple)         

      # Make sure that everything was added properly and there are no duplicates
      nose.tools.ok_(len(baseline) == len(jobs), 'the baseline has duplicate keys or tokens')
      nose.tools.ok_(len(test) == len(jobs), 'the test store has duplicate keys or tokens')

      assert baseline == test      

   def test_gevent_revoke_many(self):
      pass

class DistributedMixin(object):
   """\
   Tests to see whether keys are duplicated while updated from
   independent processes.
   """

   def test_distributed_insert(self):
      # 1) Spawn a new process with an identical shortener
      # 2) Being inserting keys in both
      # 3) Check for collisions
      # 4) Kill other process
      pass

   def test_distributed_revoke(self):   
      # Test for race conditions
      pass

class BaseStoreTest(object):  
   """\
   Tests insertion, revokation and other features of stores.

   Return the appropriate store from :meth:`make_store` when
   subclassing. The baseline is always a :class:`MemoryStore`.
   """

   # Number of iterations for the `many` tests
   many_num = 10000

   # The token generator that the baseline uses
   token_gen = TokenGen()

   # The alphabet that the baseline uses
   alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'

   def make_some_values(self, n):
      """\
      Returns a generator over a list of 26 animals, suffixed with a number

      ::

         'aardvark-0'
         'bonobo-0'
         ...
         'zebra-0'
         'aardvark-1'
         ...
      """

      animals = ['aardvark', 'bonobo', 'caiman', 'degu', 'elk', 'ferret', 'gibbon',
                 'hippopotamus', 'iguana', 'jackal', 'kangaroo', 'lemur', 'manatee',
                 'newt', 'otter', 'pike', 'quail', 'reindeer', 'stoat', 'tamarin',
                 'urchin', 'vulture', 'wombat', 'xerus', 'yak', 'zebra']

      len_animals = len(animals)
      for i in range(0, n):
         yield '{0}-{1}'.format(animals[i % len_animals], i / len_animals)

   @classmethod
   def make_store(cls):
      """\
      Return the store for a particular test here.
      """
      raise NotImplementedError

   @classmethod
   def make_baseline(cls):
      """\
      Returns the baseline store, however you want it configured.
      """
      raise NotImplementedError

   def get_store(self):
      return self.make_store()

   def get_baseline(self):
      return self.make_baseline()

   def insert_many(self):
      n = self.many_num
      baseline_store = self.get_baseline()
      store = self.get_store()
      values = self.make_some_values(n)

      keys = set()
      baseline = set()
      test = set()

      for val in values:
         baseline_key, baseline_token = baseline_store.insert(val)
         key, token = store.insert(val)

         assert baseline_key == key
         assert baseline_token == token
         assert key in store
         assert store.has_token(token)
         assert store.has_key(key)
         assert store[key] == val              
      
         baseline_triple = (baseline_key, baseline_token, val)
         triple = (key, token, val)

         assert key not in keys

         test.add(triple)
         baseline.add(baseline_triple)
         keys.add(key)

      assert baseline == test

      return baseline_store, store, test

   def test_insert_many(self):      
      self.insert_many()

   def test_revoke_many(self):
      # Insert some values
      baseline_store, store, triples = self.insert_many()
      
      # Revoke them
      for key, token, val in triples:
         store.revoke(token)
         baseline_store.revoke(token)

         assert key not in store
         assert not store.has_token(token)
         assert not store.has_key(key)
         nose.tools.assert_raises(KeyError, lambda: store[key])

   @nose.tools.nottest
   def test_insert_revoke(self, n):
      """\
      Intersperse insertions and revokations.
      """

      n = self.many_num
      baseline_store = self.get_baseline()
      store = self.get_store()
      values = list(self.make_some_values(n))

      inserted = []
      baseline_inserted = []

      revoked = []
      baseline_revoked = []

      for val in values:
         if random.randint(0,1):
            pair = store.insert(val)
            baseline_pair = baseline_store.insert(val)
            assert pair == baseline_pair
         else:
            pass
            # Choose something to revoke from the pool
            
   def test_insert_existing_key(self):
      store = self.get_store()         
      key, token = store.insert('aardvark')      

      wrap_next_formatted_pair(store, key, '')
      nose.tools.assert_raises(KeyInsertError, store.insert, 'bonobo')

   def test_insert_existing_token(self):
      store = self.get_store()
      key, token = store.insert('aardvark')      
 
      wrap_next_formatted_pair(store, '', token)
      nose.tools.assert_raises(TokenInsertError, store.insert, 'bonobo')

   def test_has_key(self):
      store = self.get_store()
      pair = store.insert('aardvark')

      assert store.has_key(pair.key)
      assert pair.key in store

   def test_has_token(self):
      store = self.get_store()      
      pair = store.insert('aardvark')
      
      assert store.has_token(pair.token)

   def test_has_no_token(self):
      store = self.get_store()
      pair = store.insert('aardvark')
      bad_token = ''

      assert not store.has_token(bad_token)

   def test_has_no_key(self):
      store = self.get_store()
      pair = store.insert('aardvark')
      bad_key = ''

      assert bad_key not in store
      assert not store.has_key(bad_key)

   def test_get_token(self):
      store = self.get_store()
      key, token = store.insert('aardvark')

      found_token = store.get_token(key)
      
      assert token == found_token
