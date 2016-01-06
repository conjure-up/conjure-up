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

from conjurelib.ui.views import ProviderView
from conjurelib.models.providers.base import ProviderModel
from .providers import MaasProviderController


class ProviderController:
    def __init__(self, common):
        self.common = common
        self.view = ProviderView(self.common,
                                 ProviderModel.available,
                                 self.render_provider_view)

    def render_provider_view(self, provider):
        """ Renders the provider specific view

        Arguments:
        provider: name of provider to use
        """
        provider = provider.lower()
        if provider == "maas":
            MaasProviderController(self.common).render()

    def render(self):
        self.common['ui'].set_header(
            title="Select a Juju provider",
            excerpt="A Juju environment is required to deploy the solution. "
            "Since no existing environments were found please "
            "select the provider you wish to use."
        )
        self.common['ui'].set_body(self.view)
