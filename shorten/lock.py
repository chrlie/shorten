try:
  import gevent.coros
  __gevent__ = True
except ImportError:
  __gevent__ = False

class Lock(object):
  def __init__(self):
    if __gevent__:
      self._lock = gevent.coros.Semaphore(2)
    else:
      self._lock = None

  def acquire(self):
    if self._lock is not None:
      self._lock.acquire()

  def release(self):
    if self._lock is not None:
      self._lock.release()

