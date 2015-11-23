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

import urwid
import asyncio

import logging

log = logging.getLogger('eventloop')


class EventLoopException(Exception):
    """ Problem with eventloop
    """
    pass


class EventLoop:

    """ Abstracts out event loop
    """
    loop = None

    @classmethod
    def build_loop(cls, ui, palette, **kwargs):
        """ Builds eventloop
        """
        extra_opts = {
            'screen': urwid.raw_display.Screen(),
            'handle_mouse': True
        }
        extra_opts['screen'].set_terminal_properties(colors=256)
        extra_opts['screen'].reset_default_terminal_palette()
        extra_opts.update(**kwargs)
        evl = asyncio.get_event_loop()
        cls.loop = urwid.MainLoop(ui, palette,
                                  event_loop=urwid.AsyncioEventLoop(loop=evl),
                                  **extra_opts)

    @classmethod
    def exit(cls, err=0):
        log.info("Stopping eventloop")
        raise urwid.ExitMainLoop()

    @classmethod
    def redraw_screen(cls):
        try:
            cls.loop.draw_screen()
        except AssertionError as e:
            log.exception("exception failure in redraw_screen")
            raise e

    @classmethod
    def set_alarm_in(cls, interval, cb):
        return cls.loop.set_alarm_in(interval, cb)

    @classmethod
    def remove_alarm(cls, handle):
        return cls.loop.remove_alarm(handle)

    @classmethod
    def run(cls):
        """ Run eventloop
        """
        try:
            cls.loop.run()
        except:
            log.exception("Exception in ev.run():")
            raise
        return
