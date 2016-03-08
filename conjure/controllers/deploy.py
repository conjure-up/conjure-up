from functools import partial
from ubuntui.ev import EventLoop
from conjure.async import AsyncPool
from conjure.juju import Juju
from conjure.api.models import model_info, model_cache_controller_provider
from conjure.charm import get_bundle
from conjure.models.charm import CharmModel
from conjure.ui.views.deploy import DeployView
from conjure.controllers.finish import FinishController

from bundleplacer.config import Config
from bundleplacer.maas import connect_to_maas
from bundleplacer.fixtures.maas import FakeMaasState
from bundleplacer.placerview import PlacerView
from bundleplacer.controller import PlacementController
import q


class DeployController:

    def __init__(self, common, controller):
        self.common = common
        self.controller, self.model = controller.split(":")
        self.controller_info = model_info(self.controller)

    def finish(self, *args):
        """ handles deployment
        """
        FinishController(self.common).render()

    def render(self):
        # Grab bundle and deploy or render placement if MAAS
        if self.controller_info['ProviderType'] == 'maas':
            bootstrap_config = model_cache_controller_provider(
                self.controller_info['ServerUUID'])
            creds = dict(
                api_host=bootstrap_config['maas-server'],
                api_key=bootstrap_config['maas-oauth'])
            q(creds)
            maas, maas_state = connect_to_maas(creds)
            bundle = get_bundle(CharmModel.to_entity(), to_file=True)
            q(bundle)
            metadata_filename = self.common['config']['metadata_filename']
            bundleplacer_cfg = Config(
                'bundle-placer',
                {'bundle_filename': bundle,
                 'metadata_filename': metadata_filename})
            q(bundleplacer_cfg)
            placement_controller = PlacementController(
                config=bundleplacer_cfg,
                maas_state=maas_state)
            q(placement_controller)
            mainview = PlacerView(placement_controller,
                                  bundleplacer_cfg,
                                  self.finish)
            q(mainview)
            self.common['ui'].set_header(
                title="Bundle Editor: {}".format(
                    self.common['config']['summary']),
                excerpt="Choose where your services should be "
                "placed in your available infrastructure"
            )
            self.common['ui'].set_subheader("Machine Placement")
            self.common['ui'].set_body(mainview)
            mainview.update()
        else:
            view = DeployView(self.common, self.finish)
            q(view)
            self.common['ui'].set_header(
                title="Deploying: {}".format(CharmModel.to_path())
            )
            self.common['ui'].set_body(view)

            # def read_status(*args):
            #     services = Juju.client.Client(request="FullStatus")
            #     services = "\n".join(services.keys())
            #     view.set_status(services)
            #     EventLoop.set_alarm_in(3, read_status)

            # def error(*args):
            #     print(args)
            # AsyncPool.submit(
            #     partial(Juju.deploy_bundle, CharmModel.to_path()))
            # EventLoop.set_alarm_in(1, read_status)
