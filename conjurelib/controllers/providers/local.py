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

from conjurelib.ui.views import LocalProviderView
from conjurelib.models.providers import LocalProviderModel
from conjurelib.juju import Juju
from conjurelib.controllers.deploy import DeployController


class LocalProviderController:
    def __init__(self, common):
        self.common = common
        self.view = LocalProviderView(self.common,
                                      self.finish)
        self.model = LocalProviderModel

    def finish(self, result):
        """ Deploys to the local provider
        """
        self.model.config.update({k: v.value for k, v in result.items()})
        Juju.create_environment(self.common['config']['juju_env'],
                                "local",
                                self.model.to_yaml())
        DeployController(self.common, self.model).render()

    def render(self):
        self.common['ui'].set_header(
            title="Local Provider",
            excerpt="Enter optional configuration items for the Local "
            "provider before deploying."
        )
        self.common['ui'].set_body(self.view)
