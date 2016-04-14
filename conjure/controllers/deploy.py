from conjure.api.models import model_info
from conjure.charm import get_bundle
from conjure.models.bundle import BundleModel
from conjure.utils import pollinate
from conjure.juju import Juju, current_controller

from bundleplacer.config import Config
from bundleplacer.maas import connect_to_maas
from bundleplacer.placerview import PlacerView
from bundleplacer.controller import PlacementController, BundleWriter


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
                controller_meta = Juju.controller_info(current_controller())
                bootstrap_config = controller_meta['bootstrap-config']
                self.app.log.debug(
                    'bootstrap_config {}'.format(bootstrap_config))
            except Exception as e:
                msg = ("Unable to query cache file, trying "
                       "alternate api: {}".format(e))
                self.app.log.error(msg)
                return self.app.ui.show_exception_message(Exception(msg))

            maasoauth = Juju.credential(bootstrap_config['cloud-type'],
                                        bootstrap_config['credential'])
            # add maas creds to env
            self.app.env['MAAS_SERVER'] = bootstrap_config['region']
            self.app.env['MAAS_OAUTH'] = maasoauth['maas-oauth']

            creds = dict(
                api_host=self.app.env['MAAS_SERVER'],
                api_key=self.app.env['MAAS_OAUTH'])
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
