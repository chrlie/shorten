# shorten
A Python library for generating short URLs.

## Installation

Install with pip: `pip install shorten`

If you want to run the tests, ensure `nose` is installed with `pip install nose`.

## The basics

Generate keys, store them. Keystores are greenlet-safe and compatible with
`gevent` and `gunicorn`.

For example, an in-memory store can be created:

```python   
   import gevent
   from shorten import shortener   

   animals = ['aardvark', 'bonobo', 'caiman', 'degu', 'elk']   

   # Create an in-memory keystore with a minimum key length of 4.
   mem_shortener = shortener(
      'memory', 
      min_length=4)

   # Request several keys at once.
   jobs = [gevent.spawn(mem_shortener.insert, animal) for animal in animals]
   gevent.joinall(jobs, timeout=2)

   # ['2112', '2111', '2114', '2113', '2115']
   print([job.value for job in jobs])
```

and a Redis-backed keystore as well!

```python   
   import redis
   from shorten import shortener

   animals = ['aardvark', 'bonobo', 'caiman', 'degu', 'elk']   

   r = redis.Redis()
   redis_shortener = shortener(
      'redis', 
      min_length=4, 
      connection=r)
   
   # ['2111', '2112', '2113', '2114', '2115']
   print([redis_shortener.insert(animal) for animal in animals])
```

## Advanced topics

Keystores can be created explicitly:

```python
   from shorten.keystores import MemoryKeystore
   from shorten.keygens import Keygen

   # Use an alternative alphabet with no similar-looking letters.
   alphabet = 'abcdefghijklmnopqrstuvwxyz23456789ABCDEFGHJKLMNPQRSTUVWXYZ'

   keygen = Keygen(alphabet=alphabet)
   shortener = MemoryKeystore(keygen)

   animals = ['aardvark', 'bonobo', 'caiman', 'degu', 'elk']

   # ['aaaa', 'aaab', 'aaac', 'aaad', 'aaae']
   print([shortener.insert(animal) for animal in animals])
```

Formatters can be used to return a modified version of the key before it is passed to the keystore.

```python
   import redis
   from shorten import shortener

   app_name = 'short.ur'

   # The redis key used to increment the current counter
   counter_key = '{0}:counter'.format(app_name)

   # A redis connection
   redis_con = redis.Redis()

   # Namespace the key to avoid junking up redis
   def formatter(key):
      return '{0}:key:{1}'.format(app_name, key)

   animals = ['aardvark', 'bonobo', 'caiman', 'degu', 'elk']   

   r = redis.Redis()
   redis_shortener = shortener(
         'redis', 
         min_length=4, 
         connection=redis_con, 
         formatter=formatter, 
         counter_key=counter_key)
   
   # ['short.ur:key:2111', 'short.ur:key:2112', 'short.ur:key:2113', 
   #  'short.ur:key:2114', 'short.ur:key:2115']
   print([redis_shortener.insert(animal) for animal in animals])
```

## Upcoming

* Tests!
* Flask middleware/routes
* MongoDB and SQLAlchemy support
