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

from conjurelib.ui.views import FinishView
from ubuntui.ev import EventLoop


class FinishController:

    def __init__(self, common):
        self.common = common
        self.view = FinishView(self.common, self.finish)

    def finish(self):
        """ handles deployment
        """
        EventLoop.exit(0)

    def render(self):
        self.common['ui'].set_header(
            title="Installing solution: {}".format(
                self.common['config']['summary']),
            excerpt="Please wait while services are being "
            "deployed."
        )
        self.common['ui'].set_body(self.view)
        # FIXME: Demo specific
        bundles = self.common['config']['bundles']
        for bundle in bundles:
            self.view.set_status("Installing {}...".format(
                bundle['name']))

        self.view.set_status("\n\n")
        self.view.set_status("Completed the install, please visit "
                             "https://jujucharms.com/docs/stable/"
                             "juju-managing to learn how to manage "
                             "your new {} solution!".format(
                                 self.common['config']['name']))
