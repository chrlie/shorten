"""\
shorten.store
~~~~~~~~~~~~~

Contains stores for different backends. Keygens for most stores are
in the same file for convenience.

Some stores will require other libraries to function.
"""

from .base import BaseStore, Pair, FormattedPair
from .memory import MemoryStore, MemoryKeygen
from .redis import RedisStore, RedisKeygen
from .memcache import MemcacheStore, MemcacheKeygen
