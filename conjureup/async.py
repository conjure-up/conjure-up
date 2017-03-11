""" Async Handler
Provides async operations for various api calls and other non-blocking
work.
"""

import logging
import time
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor
from threading import Event, RLock

log = logging.getLogger("async")


class ThreadCancelledException(Exception):
    """Exception meaning intentional cancellation"""


ShutdownEvent = Event()

_queues = defaultdict(lambda: ThreadPoolExecutor(1))
DEFAULT_QUEUE = "DEFAULT"

ENABLE_LOG = False
if ENABLE_LOG:
    import q
    _queueLog = defaultdict(OrderedDict)


def submit(func, exc_callback, queue_name="DEFAULT"):
    def cb(cb_f):
        e = cb_f.exception()
        if e:
            exc_callback(e)
        if ENABLE_LOG:
            now = time.time()
            t = _queueLog[queue_name][func]
            _queueLog[queue_name][func] = (t[0], t[1],
                                           "done", time.time(),
                                           e,
                                           "elapsed", now - t[1])
            q.q(qstatsf())
    if ShutdownEvent.is_set():
        log.debug("ignoring async.submit due to impending shutdown.")
        return None
    f = _queues[queue_name].submit(func)
    if ENABLE_LOG:
        _queueLog[queue_name][func] = ("added", time.time(), None, None, None)
        q.q(qstatsf())
    f.add_done_callback(cb)
    return f


def qstatsf():
    s = ""
    for queue, od in _queueLog.items():
        s += "{}:\n".format(queue)
        for func, t in od.items():
            s += "{} - {}\n".format(func, t)
    return s


def shutdown():
    ShutdownEvent.set()
    for queue in _queues.values():
        queue.shutdown(wait=False)


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


class Counter():
    def __init__(self):
        self.lock = RLock()
        self._value = 0

    def increment(self):
        with self.lock:
            self._value += 1

    def decrement(self):
        with self.lock:
            self._value = max(self._value - 1, 0)

    @property
    def value(self):
        return self._value

    def empty(self):
        return self.value == 0
