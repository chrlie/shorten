# coding=utf-8

import nose

import itertools
import shorten
import redis
import gevent
import random

_multiprocess_can_split_ = False

BULK_TESTS = 100

def test_instantiations():  
  """\
  Test all make_stores that can be created with `shortener`
  """

  stores = {
    'memory': {},
    'redis': {'redis': redis.Redis()},
  }

  for name in stores:
    def func():
      kwargs = stores[name]
      shorten.make_store(name, **kwargs)
      
    func.description = 'test instantiate {0}'.format(name)
    yield func

def spawn_nicely(*args):
   g = gevent.spawn(*args)
   g.link_exception(die_nicely)   
   return g

def die_nicely(*args):   
   sys.exit('greenlet died: {0}'.format(','.join(args)))

def splice_pairs(pairs, vals):
   """\
   Splice together key/token pairs and their values.

   (key, token), val -> (key, token, val)
   """

   return sorted([(key, token, val) for (key, token), val in zip(pairs, vals)])

class CommonTest(object):  

  class TokenGenerator(object):
    """\
    Just keeps a simple count.
    """

    def __init__(self):
      self.count = 0

    def create_token(self, key):
      self.count += 1
      return str(self.count)

  def make_baseline(self):
    """\
    Make the baseline for this class.
    """
   
    return shorten.make_store('memory')

  def populate_baseline(self, baseline, data, use_gevent=False):
    """\
    Insert the values into the baseline and return a zipped
    set of tuples:

      (value, key, revokation token)

    which can then be compared with another result set.
    """

    if use_gevent:   
      jobs = [spawn_nicely(baseline.insert, value) for value in data]
      gevent.joinall(jobs)
      pairs = [job.value for job in jobs]
    else: 
      pairs = map(baseline.insert, data)

    # Get the values from the baseline
    values = map(lambda pair: baseline[pair[0]], pairs)

    # Splice these together
    return splice_pairs(pairs, values)

  def make_store(self, *arg, **kwargs):
    """\
    Create a store to test for this class.
    """

    raise NotImplementedError('This should return a store for {0}'.format(self.__class__.__name__))

  def test_insert(self, N=BULK_TESTS, bulk=False, store=None):   
    #
    # Insert `N` items. The idea is that the more items that are
    # inserted, the more likely a bug will occur.
    # 
  
    store = store or self.make_store()
    baseline = self.make_baseline()

    data = [str(n) for n in xrange(0, N)]

    if bulk:
      with store.bulk() as b:
         pairs = [b.insert(value) for value in data]
    else:                                       
      pairs = [store.insert(value) for value in data]
       
    # Make sure there ARE keys and tokens
    assert len(pairs) == N

    # Make sure keys and tokens are valid
    for key, token in pairs:
      assert key is not None
      assert token is not None      
 
    values = [store[key] for key, token in pairs]

    # These are sorted
    spliced = splice_pairs(pairs, values)
    baseline_spliced = self.populate_baseline(baseline, data, use_gevent=False)

    # Ensure that there are no duplicate keys
    for s, bs in itertools.izip(spliced, baseline_spliced):
      assert s == bs      

    # Ensure that everything was inserted 
    assert set(spliced) == set(baseline_spliced)  
    assert len(spliced) == len(baseline_spliced) == len(data)

    # Are all the keys and revokation tokens present?
    for key, token in pairs:
      assert store.has_key(key)
      assert store.has_token(token)
   
      # Should not throw an error
      store.get(key)      

  def test_gevent_insert(self, N=BULK_TESTS, bulk=False, store=None):    
    #
    # Insert `N` items, just like test_insert, except gevent is used.
    # 
  
    store = store or self.make_store()
    baseline = self.make_baseline()

    data = [str(n) for n in xrange(0, N)]

    if bulk:
      with store.bulk() as b:
         jobs = [spawn_nicely(b.insert, value) for value in data]
    else:                            
      jobs = [spawn_nicely(store.insert, value) for value in data]           
 
    gevent.joinall(jobs)

    pairs = [job.value for job in jobs]  
    values = [store[key] for key, token in pairs]

    # Make sure there ARE keys and tokens
    assert len(pairs) == N

    # Make sure keys and tokens are valid
    for key, token in pairs:
      assert key is not None
      assert token is not None

    # There are sorted
    spliced = splice_pairs(pairs, values)
    baseline_spliced = self.populate_baseline(baseline, data, use_gevent=False)    

    # Ensure that everything was inserted
    assert set(spliced) == set(baseline_spliced)  
    assert len(spliced) == len(baseline_spliced) == len(data)

    # Are all the keys and revokation tokens present?
    for key, token in pairs:
      assert store.has_key(key)
      assert store.has_token(token)
   
      # Should not throw an error
      store.get(key)      

    # Ensure that there are no duplicate keys
    for s, bs in itertools.izip(spliced, baseline_spliced):
      assert s == bs

  def test_revokation(self, N=BULK_TESTS, bulk=False, store=None):    
    #
    # Test key revokation.
    # 

    SAMPLE_SIZE = N/2

    store = store or self.make_store()
    baseline = self.make_baseline()   

    class Result():
      def __init__(self, data=None, values=None, pairs=None, baseline_spliced=None):
         self.data = data
         self.values = values
         self.pairs = pairs
         self.spliced = splice_pairs(pairs, values)
         self.baseline_spliced = baseline_spliced

    def insert():
       data = [n for n in xrange(0, N)]

       if bulk:
         with store.bulk() as b:
            pairs = [b.insert(value) for value in data]
       else:                                       
         pairs = [store.insert(value) for value in data]
      
       values = [store[key] for key, token in pairs]
       baseline_spliced = self.populate_baseline(baseline, data, use_gevent=False)

       return Result(data, values, pairs, baseline_spliced)

    def revoke(result):
       pairs, baseline_spliced = result.pairs, result.baseline_spliced

       # Choose a random set of keys to revoke
       both_tokens = [(token, btoken, key) for (key, token), (bkey, btoken, bval) in zip(pairs, baseline_spliced)]
       revoke_tokens = random.sample(both_tokens, SAMPLE_SIZE)
       
       if bulk:
         with baseline.bulk() as b:
            for token, btoken, key in revoke_tokens:
               b.revoke(btoken)

         with store.bulk() as b:
            for token, btoken, key in revoke_tokens:
               b.revoke(token)
    
       else:
         for token, btoken, key in revoke_tokens:
            baseline.revoke(btoken)
            store.revoke(token)  
       
       # Have the keys really been revoked?
       for token, btoken, key in revoke_tokens:
         assert not store.has_key(key)
         assert not store.has_token(token)

         nose.tools.assert_raises(KeyError, lambda: store.revoke(token))

       return revoke_tokens
    
    first_result = insert()
    first_revoke_tokens = revoke(first_result)

    # Try inserting some new data and making sure the keys aren't reused
    second_result = insert()
 
    for token, btoken, key in first_revoke_tokens:
       assert not store.has_key(key)
        
    second_revoke_tokens = revoke(second_result)

  def test_insert_zero(self):
    self.test_insert(N=0)

  def test_insert_one(self):
    self.test_insert(N=1)    

  def test_insert_zero_bulk(self):
    self.test_insert(N=0, bulk=True)

  def test_insert_one_bulk(self):
    self.test_insert(N=1, bulk=True) 
  
  def test_insert_bulk(self):
    self.test_insert(bulk=True) 

  def test_gevent_insert_zero(self):
    self.test_gevent_insert(N=0)

  def test_gevent_insert_one(self):
    self.test_gevent_insert(N=1)  

  def test_insert_bulk_10K(self):
    self.test_insert(N=10000, bulk=True)      

  def test_gevent_insert_10K(self):
    self.test_gevent_insert(N=10000)

#  def test_gevent_revokation(self):
#    pass
  
#  def test_custom_token_generator(self):
#    pass

  def test_revoke_zero(self):
    self.test_revokation(N=0)

#  def test_revoke_10K(self):
#    self.test_revokation(N=10000)

#  def test_revok_1M(self):
#    self.test_revokation(N=1000000)

class TestMemory(CommonTest):

  def make_store(self):
    return shorten.make_store('memory')

class TestRedis(CommonTest):

  redis_namespace = 'shorten:nosetests'
  redis_counter_key = 'shorten:nosetests:counter'
  redis = redis.Redis()

  class Formatter(shorten.Formatter):
    def format_key(self, key):
      return '{0}:key:{1}'.format(TestRedis.redis_namespace, key)

    def format_token(self, token):
      return '{0}:revokation_token:{1}'.format(TestRedis.redis_namespace, token)

  def make_store(self):
    formatter = self.Formatter()
    return shorten.make_store('redis', redis=self.redis,
                                       redis_counter_key=self.redis_counter_key,
                                       formatter=formatter)

  def make_baseline(self):
    formatter = self.Formatter()
    return shorten.make_store('memory', formatter=formatter)

  def clear_redis(self, pattern='*'):
    """\
    Clear redis of namespaced keys
    """  

    r = redis.Redis()
    to_del = r.keys('{0}:{1}'.format(self.redis_namespace, pattern))
       
    with r.pipeline() as p:
      for key in to_del:
         p.delete(key)
      p.execute()

  def setUp(self):
    self.clear_redis()
       
  def tearDown(self):
    self.clear_redis()       
