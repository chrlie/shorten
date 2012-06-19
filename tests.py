# coding=utf-8

import nose

import itertools
import shorten
import redis
import gevent
import uuid

_multiprocess_can_split_ = False

def redis_prefix(val):
  return 'shorten:nosetests:{0}'.format(val)

def key_formatter(token):
  return redis_prefix('key:{0}'.format(token))

def test_instantions():  
  map = {
    'memory' : ([], {}),
    'redis'  : ([], {'redis' : redis.Redis()}),
  }

  for name in map:
    def func():
      args, kwargs = map[name]
      shorten.shortener(name, *args, **kwargs)
      
    func.description = 'test instantiate {0}'.format(name)
    yield func

class CommonTest(object):  
  def populate_baseline(self, vals, use_gevent=False):
    if use_gevent:   
      # TODO: prevent exceptions in the greenlets from breaking nose
      jobs = [gevent.spawn(self.baseline.insert, v) for v in vals]
      gevent.joinall(jobs)
      keys = [job.value for job in jobs]
    else: 
      keys = map(self.baseline.insert, vals)
      
    vals = map(lambda k: self.baseline[k], keys)
    return zip(keys, vals)

class TestMemory(CommonTest):
  def make_baseline(self):
    return shorten.shortener('memory')

  def setUp(self):
    self.baseline = self.make_baseline()

  def test_insert_zero(self):
    self.test_insert(N=0)

  def test_insert_one(self):
    self.test_insert(N=1)    

  def test_insert(self, N=10000, use_multi=False):
    original_vals = [n for n in xrange(0, N)]
  
    store = shorten.shortener('memory')

    if use_multi:
      # This returns an iterator, so iterate
      keys = [key for key in store.insert_multi(*original_vals)]
    else:                                       
      keys = [store.insert(v) for v in original_vals]  
      
    vals = [store[key] for key in keys]

    kv = zip(keys, vals)        
    baseline_kv = self.populate_baseline(original_vals, use_gevent=False)
    
    assert set(kv) == set(baseline_kv)     

  def test_insert_zero_multi(self):
    self.test_insert(N=0, use_multi=True)

  def test_insert_one_multi(self):
    self.test_insert(N=1, use_multi=True) 

  def test_insert_multi(self):
    self.test_insert(use_multi=True) 

  def test_gevent_insert_zero(self):
    self.test_gevent_insert(N=0)

  def test_gevent_insert_one(self):
    self.test_gevent_insert(N=1)  

  def test_gevent_insert(self, N=10000, use_multi=False):
    original_vals = [n for n in xrange(0, N)]
  
    store = shorten.shortener('memory')
    
    if use_multi:
      job = gevent.spawn(lambda: store.insert_multi(*original_vals))
      gevent.joinall([job])
      keys = [key for key in job.value]
    else:
      jobs = [gevent.spawn(store.insert, v) for v in original_vals]
      gevent.joinall(jobs)
      keys = [job.value for job in jobs]
    
    vals = [store[key] for key in keys]

    kv = zip(keys, vals)        
    baseline_kv = self.populate_baseline(original_vals, use_gevent=True)
    
    assert set(kv) == set(baseline_kv)  

  def test_gevent_insert_zero_multi(self):
    self.test_gevent_insert(N=0, use_multi=True)

  def test_gevent_insert_one_multi(self):
    self.test_gevent_insert(N=1, use_multi=True)  

  def test_gevent_insert_multi(self):
    self.test_gevent_insert(use_multi=True)  

  def test_bulk_next(self, N=1):
    single_kg = shorten.keygens.MemoryKeygen()
    bulk_kg = shorten.keygens.MemoryKeygen()
    
    single_keys = [single_kg.next()[0] for i in xrange(0, N)]
    bulk_keys = [key for key in bulk_kg.next(N)]

    assert single_keys == bulk_keys

  def test_key_revokation(self, N=10000):
    original_vals = [str(n) for n in xrange(0, N)]
    
    # Revokation tokens are just integers
    def get_revokation_token():
      c = 0
      while True:
        yield c
        c += 1
    
    store = shorten.shortener('memory')                                     

    vals_and_rev_tokens = itertools.izip(original_vals, iter(get_revokation_token()))
    rev_tokens = []
    keys = []
    
    for (val, rev) in vals_and_rev_tokens:
       rev_tokens.append(rev)
       keys.append(store.insert_with_revoke(val, rev))

    vals = [store[key] for key in keys]      
    
    kv = zip(keys, vals)        
    baseline_kv = self.populate_baseline(original_vals, use_gevent=False)    
    
    assert set(kv) == set(baseline_kv)            

    # Revoke all the keys and make sure    
    map(store.revoke, rev_tokens)

    # 1. the values are actually deleted    
    for key in keys:
      nose.tools.assert_raises(KeyError, lambda: store[key])

    # 2. the old keys are not reused
    baseline = self.make_baseline()
    first_expected_key = baseline.insert('sentinel-test_key_revokation')
    reinserted_key = store.insert('sentinel-test_key_revokation')
    
    assert reinserted_key not in set(keys)

class TestRedis(CommonTest):
  counter_key = redis_prefix('counter')

  @classmethod
  def setup_class(cls):
    pass
  
  @classmethod
  def teardown_class(cls):
    pass

  def clear_redis(self, pattern='*'):
    """Clear redis of namespaced keys"""  
    r = redis.Redis()
    to_del = r.keys(redis_prefix(pattern))
    p = r.pipeline()
    
    for key in to_del:
      p.delete(key)
      
    p.execute()    

  def populate_baseline(self, vals, use_gevent=False):
    if use_gevent:   
      # TODO: prevent exceptions in the greenlets from breaking nose
      jobs = [gevent.spawn(self.baseline.insert, v) for v in vals]
      gevent.joinall(jobs)
      keys = [job.value for job in jobs]
    else: 
      keys = map(self.baseline.insert, vals)
      
    vals = map(lambda k: self.baseline[k], keys)
    return zip(keys, vals)

  def make_baseline(self):
    return shorten.shortener('memory', formatter=key_formatter)

  def setUp(self):
    self.clear_redis()
    self.baseline = self.make_baseline()
       
  def tearDown(self):
    self.clear_redis()       

  def test_insert_zero(self):
    self.test_insert(N=0)

  def test_insert_one(self):
    self.test_insert(N=1)    

  def test_insert(self, N=10000, use_multi=False):
    # Redis won't preserve ints from python
    original_vals = [str(n) for n in xrange(0, N)]
  
    store = shorten.shortener('redis', redis=redis.Redis(), 
                                       formatter=key_formatter, 
                                       counter_key=self.counter_key)  

    if use_multi:
      keys = [key for key in store.insert_multi(*original_vals)]
    else:                                       
      keys = [store.insert(v) for v in original_vals]    
      
    vals = [store[key] for key in keys]

    kv = zip(keys, vals)        
    baseline_kv = self.populate_baseline(original_vals, use_gevent=False)    
    
    assert set(kv) == set(baseline_kv)     

  def test_insert_zero_multi(self):
    self.test_insert(N=0, use_multi=True)

  def test_insert_one(self):
    self.test_insert(N=1, use_multi=True)

  def test_insert_multi(self):
    self.test_insert(use_multi=True)   

  def test_gevent_insert_zero(self):
    self.test_gevent_insert(N=0)

  def test_gevent_insert_one(self):
    self.test_gevent_insert(N=1)  
       
  def test_gevent_insert(self, N=10000, use_multi=False):
    original_vals = [str(n) for n in xrange(0, N)]
    
    store = shorten.shortener('redis', redis=redis.Redis(), 
                                       formatter=key_formatter, 
                                       counter_key=self.counter_key)  

    if use_multi:
      job = gevent.spawn(lambda: store.insert_multi(*original_vals))
      gevent.joinall([job])
      keys = [key for key in job.value]
    else:
      jobs = [gevent.spawn(store.insert, val) for val in original_vals]
      gevent.joinall(jobs)
      keys = [job.value for job in jobs]    

    vals = [store[key] for key in keys]

    kv = zip(keys, vals)    
    baseline_kv = self.populate_baseline(original_vals, use_gevent=True)

    assert set(kv) == set(baseline_kv)

  def test_gevent_insert_zero_multi(self):
    self.test_gevent_insert(N=0, use_multi=True)

  def test_gevent_insert_one_multi(self):
    self.test_gevent_insert(N=1, use_multi=True)  

  def test_gevent_insert_multi(self):
    self.test_gevent_insert(use_multi=True)  

  def test_key_revokation_one(self):
    # Use this if you don't want to print out 10000 errors
    
    store = shorten.shortener('redis', redis=redis.Redis(), 
                                       formatter=key_formatter, 
                                       counter_key=self.counter_key)         
    
    revoke_token = 'sentinel-test_key_revokation_one-revoke-token'
    val = 'sentinel-test_key_revokation_one-revoke'
    
    key = store.insert_with_revoke(val, revoke_token)
    store.revoke(revoke_token)
    
    nose.tools.assert_raises(KeyError, lambda: store[key])
    
  def test_key_revokation(self, N=10000):
    original_vals = [str(n) for n in xrange(0, N)]
    
    # Revokation tokens are just integers
    def get_revokation_token():
      c = 0
      while True:
        yield c
        c += 1
    
    store = shorten.shortener('redis', redis=redis.Redis(), 
                                       formatter=key_formatter, 
                                       counter_key=self.counter_key)  

    vals_and_rev_tokens = itertools.izip(original_vals, iter(get_revokation_token()))
    rev_tokens = []
    keys = []
    
    # TODO: test with a pipeline
    for (val, rev) in vals_and_rev_tokens:
       rev_tokens.append(rev)
       keys.append(store.insert_with_revoke(val, rev))
    
    #key_iter = itertools.starmap(store.insert_with_revoke, vals_and_rev_tokens)    
    #keys = [k for k in key_iter]    
    
    vals = [store[key] for key in keys]      
    
    kv = zip(keys, vals)        
    baseline_kv = self.populate_baseline(original_vals, use_gevent=False)    
    
    assert set(kv) == set(baseline_kv)            

    # Revoke all the keys and make sure    
    map(store.revoke, rev_tokens)

    # 1. the values are actually deleted    
    for key in keys:
      nose.tools.assert_raises(KeyError, lambda: store[key])

    # 2. the old keys are not reused
    baseline = self.make_baseline()
    first_expected_key = baseline.insert('sentinel-test_key_revokation')
    reinserted_key = store.insert('sentinel-test_key_revokation')
    
    assert reinserted_key not in set(keys)
          
