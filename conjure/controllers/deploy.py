from conjure.api.models import model_info
from conjure.charm import get_bundle
from conjure.models.bundle import BundleModel
from conjure.utils import pollinate
from conjure.juju import Juju, current_controller

from bundleplacer.config import Config
from bundleplacer.maas import connect_to_maas

from bundleplacer.controller import PlacementController, BundleWriter
from bundleplacer.charmstore_api import MetadataController

from conjure.ui.views.service_walkthrough import ServiceWalkthroughView


class DeployController:

    def __init__(self, app):
        self.app = app
        self.placement_controller = None
        self.bundle_filename = None

    def finish(self, back=False):
        """ handles deployment

        Arguments:
        back: if true returns to previous controller
        """
        if back:
            return self.app.controllers['jujucontroller'].render()

        bw = BundleWriter(self.placement_controller)
        bw.write_bundle(self.bundle_filename)
        pollinate(self.app.session_id, 'PC', self.app.log)
        self.app.controllers['deploysummary'].render(self.bundle_filename)

    def render(self, model):
        self.app.current_model = model
        info = model_info(self.app.current_model)

        # Set our provider type environment var so that it is
        # exposed in future processing tasks
        self.app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']

        # Grab bundle and deploy or render placement if MAAS
        try:
            self.bundle_filename = get_bundle(BundleModel.to_entity(),
                                              to_file=True)
        except Exception as e:
            return self.app.ui.show_exception_message(e)

        metadata_filename = self.app.config['metadata_filename']
        config_filename = self.app.config['config_filename']

        bundleplacer_cfg = Config(
            'bundle-placer',
            {'bundle_filename': self.bundle_filename,
             'metadata_filename': metadata_filename,
             'config_filename': config_filename,
             'bundle_key': BundleModel.key(),
             'provider_type': info['ProviderType']})

        self.placement_controller = PlacementController(
            maas_state=None,
            config=bundleplacer_cfg)

        self.app.metadata_controller = MetadataController(
            self.placement_controller, bundleplacer_cfg)

        dwv = ServiceWalkthroughView(self.app,
                                     self.placement_controller,
                                     self.finish)
        
        self.app.ui.set_subheader("Service Walkthrough")
        self.app.ui.set_body(dwv)
        dwv.update()
