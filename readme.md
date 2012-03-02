# shorten
A Python library for generating short URLs.

## The basics

Generate keys, store them.

```python
   from shorten import Shortener
   
   # Create a shortener with a sequential key generator
   # (starting at a minimum length of 4 digits) stored
   # in memory
   shortener = Shortener()
   
   # Insert a key
   key = shortener.insert('https://github.com')
   
   # 2111
   print(key)
   
   # https://github.com
   print(shortener[key])
```

## What doesn't work

All keys are stored in memory. Gevent will cause synchronization issues.
