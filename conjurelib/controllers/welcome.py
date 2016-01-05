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

from conjurelib.ui.views import WelcomeView
from conjurelib.models.charm import CharmModel
from conjurelib.juju import Juju


class WelcomeController:
    def __init__(self, common):
        self.common = common
        self.view = WelcomeView(self.common, self.finish)

    def finish(self, msg):
        """ Finalizes welcome controller

        Arguments:
        name: name of charm/bundle to use
        config: config options to pass to juju deploy
        """
        # model = CharmModel(name, config)
        # if not Juju.available():
        #     print("Taking you to juju controller")
        # else:
        #     print("Taking you to finalize controller")
        print(msg)

    def render(self):
        config = self.common['config']
        self.common['ui'].set_header(
            title="Install {}".format(config['name']),
            excerpt=config['summary']
        )
        self.common['ui'].set_body(self.view)
