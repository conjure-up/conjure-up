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

import time
from ubuntui.ev import EventLoop
from conjurelib.charm import get_bundle
from conjurelib.models.charm import CharmModel
from conjurelib.ui.views import DeployView
from conjurelib.controllers.finish import FinishController

from bundleplacer.config import Config
from bundleplacer.fixtures.maas import FakeMaasState
from bundleplacer.placerview import PlacerView
from bundleplacer.controller import PlacementController


class DeployController:

    def __init__(self, common, provider):
        self.common = common
        self.provider = provider

    def finish(self, *args):
        """ handles deployment
        """
        FinishController(self.common).render()

    def render(self):
        # Grab bundle and deploy or render placement if MAAS
        if self.provider.name.lower() == "local":
            view = DeployView(self.common, self.provider, self.finish)
            self.common['ui'].set_header(
                title="Deploying: {}".format(CharmModel.to_path())
            )
            self.common['ui'].set_body(view)

            def stfu(*args):
                view.set_status(time.asctime())
                EventLoop.set_alarm_in(1, stfu)
            EventLoop.set_alarm_in(1, stfu)

        # TODO: demo specific should be changed afterwards
        if self.provider.name.lower() == "maas":
            bundle = get_bundle(CharmModel.to_entity())
            bundleplacer_cfg = Config(
                'bundle-placer',
                {'bundle': bundle,
                 'metadata': self.common['config']['metadata']})
            placement_controller = PlacementController(
                config=bundleplacer_cfg,
                maas_state=FakeMaasState())
            mainview = PlacerView(placement_controller,
                                  bundleplacer_cfg,
                                  self.finish)
            self.common['ui'].set_header(
                title="Bundle Editor: {}".format(
                    self.common['config']['summary']),
                excerpt="Choose where your services should be "
                "placed in your available infrastructure"
            )
            self.common['ui'].set_subheader("Machine Placement")
            self.common['ui'].set_body(mainview)
            mainview.update()
