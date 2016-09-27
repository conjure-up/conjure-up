# Copyright 2015 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Async Handler
Provides async operations for various api calls and other non-blocking
work.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event

log = logging.getLogger("bundleplacer.async")


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
    return f


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
