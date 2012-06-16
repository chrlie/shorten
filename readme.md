# shorten

A Python library for generating short URLs.
It's gevent-safe, so you can use it with Gunicorn (and consequently Flask, Django and Pyramid).

## Installation

Install with pip: `pip install shorten`

If you want to run the tests, ensure `nose` is installed with `pip install nose`.

## The basics

Make a shortener:

```python
   import shorten
   import redis
   
   shortener = shorten.shortener('redis', redis=redis.Redis())
```

Map a short key to a long value:

```python
   # '2111'
   key = shortener.insert('http://mitpress.mit.edu/sicp/full-text/book/book.html')
```   

Map multiple keys and values from greenlets:

```python
   import gevent   

   values = [
    'aardvark', 
    'bonobo', 
    'caiman', 
    'degu', 
    'elk',
   ]
      
   jobs = [gevent.spawn(shortener.insert, v) for v in values]   
   keys = map(lambda j: j.value, gevent.joinall(jobs, timeout=2))
   
   # ['2111', '2112', '2114', '2113', '2115']
   print(keys)
```  

If you wish to store the keys with some sort of prefix, pass in a `formatter` function when a `KeyStore` is created:

```python
   import shorten
   import redis
   
   def to_key_format(token):
      return 'my:namespace:key:{0}'.format(token)
   
   shortener = shorten.shortener('redis', redis=redis.Redis(), formatter=to_key_format)
   
   # 'my:namespace:key:2111'
   key = shortener.insert('http://mitpress.mit.edu/sicp/full-text/book/book.html')
```      

Custom alphabets of symbols (any 0-index based iterable) can be passed to the `shortener` function too:

```python
   import shorten

   # Use an alternative alphabet with faces
   alphabet = [
    ':)', ':(', ';)', ';(', '>:)', ':D', ':x', ':X', ':|', ':O', '><', '<<', '>>', '^^', 'O_o', u'?_?',
   ]

   shortener = shorten.shortener('memory', alphabet=alphabet)

   values = [
    'aardvark', 
    'bonobo', 
    'caiman', 
    'degu', 
    'elk',
   ]
   
   keys = map(shortener.insert, values)
   
   # [':(:):):)', ':(:):):(', ':(:):);)', ':(:):);(', ':(:):)>:)']
   print(keys)
```

Formatters can be used to return a modified version of the key before it is passed to the keystore.

```python
   import redis
   from shorten import shortener

   app_name = 'short.ur'

   # The redis key used to increment the current counter
   counter_key = '{0}:counter'.format(app_name)

   # A redis redis
   redis_con = redis.Redis()

   # Namespace the key to avoid junking up redis
   def formatter(key):
      return '{0}:key:{1}'.format(app_name, key)

   animals = ['aardvark', 'bonobo', 'caiman', 'degu', 'elk']   

   r = redis.Redis()
   redis_shortener = shortener(
         'redis', 
         min_length=4, 
         redis=redis_con, 
         formatter=formatter, 
         counter_key=counter_key)
   
   # ['short.ur:key:2111', 'short.ur:key:2112', 'short.ur:key:2113', 
   #  'short.ur:key:2114', 'short.ur:key:2115']
   print([redis_shortener.insert(animal) for animal in animals])
```