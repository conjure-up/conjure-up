# Copyright (c) 2015 Canonical Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
