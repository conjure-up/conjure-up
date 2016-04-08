from conjure.api.models import model_info, model_cache_controller_provider
from conjure.charm import get_bundle
from conjure.models.bundle import BundleModel
from conjure.utils import pollinate

from bundleplacer.config import Config
from bundleplacer.maas import connect_to_maas
from bundleplacer.placerview import PlacerView
from bundleplacer.controller import PlacementController, BundleWriter

from urllib.parse import urlparse


class DeployController:

    def __init__(self, app):
        self.app = app
        self.placement_controller = None
        self.bundle = None

    def finish(self, back=False):
        """ handles deployment

        Arguments:
        back: if true returns to previous controller
        """
        if back:
            return self.app.controllers['jujucontroller'].render()

        bw = BundleWriter(self.placement_controller)
        bw.write_bundle(self.bundle)
        pollinate(self.app.session_id, 'PC', self.app.log)
        self.app.controllers['deploysummary'].render(self.bundle)

    def render(self, model):
        self.app.current_model = model
        info = model_info(self.app.current_model)

        # Set our provider type environment var so that it is
        # exposed in future processing tasks
        self.app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']

        # Grab bundle and deploy or render placement if MAAS
        self.bundle = get_bundle(BundleModel.to_entity(), to_file=True)
        metadata_filename = self.app.config['metadata_filename']

        bundleplacer_cfg = Config(
            'bundle-placer',
            {'bundle_filename': self.bundle,
             'metadata_filename': metadata_filename,
             'config_filename': self.app.argv.build_conf,
             'bundle_key': BundleModel.key(),
             'provider_type': info['ProviderType']})

        if info['ProviderType'] == 'maas':
            pollinate(self.app.session_id, 'PM', self.app.log)
            try:
                bootstrap_config = model_cache_controller_provider(
                    info['ServerUUID'])
            except Exception as e:
                msg = ("Unable to query cache file, trying "
                       "alternate api: {}".format(e))
                self.app.log.error(msg)
                return self.app.ui.show_exception_message(Exception(msg))
            maas_server = urlparse(bootstrap_config['maas-server'])

            # add maas creds to env
            self.app.env['MAAS_SERVER'] = maas_server.hostname
            self.app.env['MAAS_OAUTH'] = bootstrap_config['maas-oauth']

            creds = dict(
                api_host=maas_server.hostname,
                api_key=bootstrap_config['maas-oauth'])
            maas, maas_state = connect_to_maas(creds)
            self.placement_controller = PlacementController(
                config=bundleplacer_cfg,
                maas_state=maas_state)
            mainview = PlacerView(self.placement_controller,
                                  bundleplacer_cfg,
                                  self.finish, has_maas=True)
            self.app.ui.set_header(
                title=self.app.config['summary'],
                excerpt=("Place services, add additional charms, and manage "
                         "service relations")
            )
            self.app.ui.set_subheader("Bundle Editor")
            self.app.ui.set_body(mainview)
            mainview.update()
        else:
            pollinate(self.app.session_id, 'PS', self.app.log)
            self.placement_controller = PlacementController(
                config=bundleplacer_cfg)
            mainview = PlacerView(self.placement_controller,
                                  bundleplacer_cfg,
                                  self.finish)
            self.app.ui.set_header(
                title=self.app.config['summary'],
                excerpt=("Add additional charms and manage service relations")
            )
            self.app.ui.set_subheader("Bundle Editor")
            self.app.ui.set_body(mainview)
            mainview.update()
