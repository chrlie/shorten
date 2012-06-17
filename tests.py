# coding=utf-8
# Sorry, the tests are a mess for now

import itertools
import shorten
import redis
import gevent

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
  def setUp(self):
    self.baseline = shorten.shortener('memory')

  def test_insert_zero(self):
    self.test_insert(N=0)

  def test_insert_one(self):
    self.test_insert(N=1)    

  def test_insert(self, N=10000):
    original_vals = [n for n in xrange(0, N)]
  
    store = shorten.shortener('memory')
    keys = [store.insert(v) for v in original_vals]    
    vals = [store[key] for key in keys]

    kv = zip(keys, vals)        
    baseline_kv = self.populate_baseline(original_vals, use_gevent=False)
    
    assert set(kv) == set(baseline_kv)     

  def test_gevent_insert_zero(self):
    self.test_gevent_insert(N=0)

  def test_gevent_insert_one(self):
    self.test_gevent_insert(N=1)  

  def test_gevent_insert(self, N=10000):
    original_vals = [n for n in xrange(0, N)]
  
    store = shorten.shortener('memory')
    jobs = [gevent.spawn(store.insert, v) for v in original_vals]
    gevent.joinall(jobs)
    keys = [job.value for job in jobs]
    vals = [store[key] for key in keys]

    kv = zip(keys, vals)        
    baseline_kv = self.populate_baseline(original_vals, use_gevent=True)
    
    assert set(kv) == set(baseline_kv)  

  def test_bulk_next(self, N=1):
    single_kg = shorten.keygens.MemoryKeygen()
    bulk_kg = shorten.keygens.MemoryKeygen()
    
    single_keys = [single_kg.next()[0] for i in xrange(0, N)]
    bulk_keys = [key for key in bulk_kg.next(N)]

    assert single_keys == bulk_keys

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

  def setUp(self):
    self.clear_redis()
    self.baseline = shorten.shortener('memory', formatter=key_formatter)
       
  def tearDown(self):
    self.clear_redis()       

  def test_insert_zero(self):
    self.test_insert(N=0)

  def test_insert_one(self):
    self.test_insert(N=1)    

  def test_insert(self, N=10000):
    # Redis won't preserve ints from python
    original_vals = [str(n) for n in xrange(0, N)]
  
    store = shorten.shortener('redis', redis=redis.Redis(), 
                                       formatter=key_formatter, 
                                       counter_key=self.counter_key)  
                                       
    keys = [store.insert(v) for v in original_vals]    
    vals = [store[key] for key in keys]

    kv = zip(keys, vals)        
    baseline_kv = self.populate_baseline(original_vals, use_gevent=False)    
    
    assert set(kv) == set(baseline_kv)     

  def test_gevent_insert_zero(self):
    self.test_gevent_insert(N=0)

  def test_gevent_insert_one(self):
    self.test_gevent_insert(N=1)  
       
  def test_gevent_insert(self, N=10000):
    original_vals = [str(n) for n in xrange(0, N)]
    
    store = shorten.shortener('redis', redis=redis.Redis(), 
                                       formatter=key_formatter, 
                                       counter_key=self.counter_key)  
                                       
    job = gevent.spawn(lambda: store.insert_multi(*original_vals))
    gevent.joinall([job])
    keys = job.value

    vals = [store[key] for key in keys]

    kv = zip(keys, vals)    
    baseline_kv = self.populate_baseline(original_vals, use_gevent=True)
    
    assert set(kv) == set(baseline_kv)
