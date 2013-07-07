import redis
import nose

import shorten
from common import BaseStoreTest, GeventTestMixin

NAMESPACE = 'shorten:nose_tests'
COUNTER_KEY = 'shorten:nose_tests:counter'

class Formatter(object):
   def format_key(self, key):
      return '{ns}:keys:{key}'.format(ns=NAMESPACE, key=key)

   def format_token(self, token):
      return '{ns}:tokens:{token}'.format(ns=NAMESPACE, token=token)

def clear_redis(connection=None, pattern='*'):
   """\
   Clear redis of namespaced keys
   """  

   conn = connection or redis.Redis()
   to_del = conn.keys('{0}:{1}'.format(NAMESPACE, pattern))
      
   with conn.pipeline() as p:
      for key in to_del:
         p.delete(key)
      p.execute()

def test_make_store():
   conn = redis.Redis()
   store = shorten.make_store('redis', redis_client=conn, counter_key=COUNTER_KEY)   

   assert store
   assert isinstance(store, shorten.RedisStore)

def test_formatter():
   key = 'test'
   formatter = Formatter()
   fkey = formatter.format_key(key)

   assert fkey != key

class TestRedisStore(BaseStoreTest, GeventTestMixin):
   many_num = 1000
   formatter = Formatter()

   @classmethod
   def setup_class(cls):
      cls.redis = redis.StrictRedis()

   @classmethod
   def teardown_class(cls):
      clear_redis(cls.redis)

   @classmethod
   def make_store(cls):
      conn = cls.redis

      store = shorten.RedisStore( 
            redis_client=conn, 
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
      clear_redis(self.redis)

   def test_formatted_key_inserted_into_redis(self):
      store = self.get_store()      
      key, token = store.insert('aardvark')      

      formatted_key = store.formatter.format_key(key)    
      redis_val = self.redis.hget(formatted_key, 'value')

      assert redis_val == 'aardvark'   

