import pylibmc
import shorten
import nose

from common import BaseStoreTest, GeventTestMixin

NAMESPACE = 'shorten:nose_tests'
COUNTER_KEY = 'shorten:nose_tests:counter_key'

class Formatter(object):
   def format_key(self, key):
      return '{ns}:keys:{key}'.format(ns=NAMESPACE, key=key)

   def format_token(self, token):
      return '{ns}:tokens:{token}'.format(ns=NAMESPACE, token=token)

def test_make_store():
   conn = pylibmc.Client(['127.0.0.1'], binary=True,
      behaviors={'tcp_nodelay': True, 'ketama': True})

   store = shorten.make_store('memcache', memcache_client=conn, counter_key=COUNTER_KEY)   

   assert store
   assert isinstance(store, shorten.MemcacheStore)

class TestMemcacheStore(BaseStoreTest, GeventTestMixin):
   many_num = 1
   formatter = Formatter()

   @classmethod
   def setup_class(cls):
      cls.mc = pylibmc.Client(['127.0.0.1'], binary=True,
            behaviors={'tcp_nodelay': True, 'ketama': True})

   @classmethod
   def teardown_class(cls):
      cls.mc.flush_all()

   @classmethod
   def make_store(cls):      
      store = shorten.MemcacheStore(
            memcache_client=cls.mc,
            counter_key=COUNTER_KEY,
            token_gen=cls.token_gen, 
            formatter=cls.formatter, 
            start=0,
            alphabet=cls.alphabet)

      return store

   @classmethod
   def make_baseline(cls):
      store = shorten.MemoryStore(
            token_gen=cls.token_gen,
            formatter=cls.formatter,
            start=0,
            alphabet=cls.alphabet)

      return store

   def tearDown(self):
      self.mc.flush_all()

