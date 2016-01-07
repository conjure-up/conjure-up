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

from ubuntui.dialog import Dialog
from ubuntui.ev import EventLoop
from ubuntui.widgets import StringEditor


class LocalProviderView(Dialog):

    input_items = [
        ('apt-http-proxy', 'APT HTTP Proxy: ', StringEditor()),
        ('apt-https-proxy', 'APT HTTPS Proxy: ', StringEditor()),
        ('http-proxy', 'HTTP Proxy: ', StringEditor()),
        ('https-proxy', 'HTTPS Proxy: ', StringEditor())
    ]

    def __init__(self, common, cb):
        self.common = common
        title = "Local Configuration"
        super().__init__(title, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
