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
import os
import subprocess
import errno
import fcntl
from tornado.ioloop import IOLoop

BUFSIZ = 1024

log = logging.getLogger("async")


AsyncPool = ThreadPoolExecutor(1)
log.debug('AsyncPool={}'.format(AsyncPool))


def _set_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)


def check_output(call, callback):
    """ A non-blocking version of subprocess.check_output
    on the tornado ioloop.
    """
    ioloop = IOLoop.instance()
    out_r, out_w = os.pipe()
    nul_f = open(os.devnull, 'w')
    p = subprocess.Popen(call, stdout=out_w, stderr=nul_f)
    nul_f.close()
    os.close(out_w)
    _set_nonblocking(out_r)
    data = []

    def _poll():
        if p.returncode is None:
            p.poll()

        if p.returncode is not None:
            ioloop.remove_handler(out_r)
            os.close(out_r)

            callback("".join(data), p.returncode)

    def _handle_read(fd, events):
        if events & ioloop.READ:
            try:
                buf = os.read(out_r, BUFSIZ)
            except (IOError, OSError) as e:
                if e.args[0] == errno.EBADF:
                    _poll()
                elif e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise

            if not buf:
                _poll()
            else:
                data.append(buf)

        if events & ioloop.ERROR:
            _poll()

    ioloop.add_handler(out_r, _handle_read,
                       ioloop.ERROR | ioloop.READ)
