.. shorten documentation master file, created by
   sphinx-quickstart on Mon Jun 10 19:35:28 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


===================

Shorten is a key-value store with auto-generating keys. Use it for a private 
URL shortener.

I made this library after finding a whole bunch of snippets like this:

::

   def encode(

Or even worse, some clever enumeration through bit-shifting

::


Or even *worse*, schemes whose keys are dependent on the input data!
   


Some stores require external libraries.

Contents:

.. toctree::
   :maxdepth: 2

.. autofunction:: shorten.make_store

.. automodule:: shorten.store.redis
   :members:

# .. automodule:: shorten.key
#   :members:

# .. automodule:: shorten.token
#   :members:
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

