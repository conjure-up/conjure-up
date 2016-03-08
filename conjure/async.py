""" Async Handler
Provides async operations for various api calls and other non-blocking
work.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import time
log = logging.getLogger("async")


class ThreadCancelledException(Exception):
    """Exception meaning intentional cancellation"""

AsyncPool = ThreadPoolExecutor(1)
log.debug('AsyncPool={}'.format(AsyncPool))


ShutdownEvent = Event()


def submit(func, exc_callback):
    def cb(cb_f):
        e = cb_f.exception()
        if e:
            exc_callback(e)
    if ShutdownEvent.is_set():
        log.debug("ignoring async.submit due to impending shutdown.")
        return
    f = AsyncPool.submit(func)
    f.add_done_callback(cb)


def shutdown():
    ShutdownEvent.set()
    AsyncPool.shutdown(wait=False)


def sleep_until(s):
    """returns after 's' seconds.
    If the ShutdownEvent is raised before the wait is over,
    raises a ThreadCancelledException.
    """
    start = time.time()
    while not ShutdownEvent.wait(timeout=.1):
        if time.time() - start >= s:
            return True
    raise ThreadCancelledException("Thread cancelled while sleeping")
