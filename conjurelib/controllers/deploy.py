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

from conjurelib.ui.views import DeployView
from conjurelib.models import CharmModel
from conjurelib import async
from conjurelib.utils import APT
from functools import partial


class DeployController:

    def __init__(self, common, provider):
        self.common = common
        self.provider = provider
        self.view = DeployView(self.common, self.provider, self.finish)
        if provider.name == "local":
            async.submit(partial(APT.install, ['juju-local']),
                         self.common['ui'].show_exception_message)
        else:
            async.submit(partial(APT.install, ['juju']),
                         self.common['ui'].show_exception_message)

    def finish(self):
        """ handles deployment
        """
        print("Deployed: juju deploy {}".format(CharmModel.to_path()))

    def render(self):
        config = self.common['config']
        self.common['ui'].set_header(
            title=config['summary'],
            excerpt="Please wait, deploying your solution: "
            "juju deploy {}".format(CharmModel.to_path())
        )
        self.common['ui'].set_body(self.view)
