from conjure.api.models import model_info, model_cache_controller_provider
from conjure.charm import get_bundle
from conjure.models.bundle import BundleModel
from conjure.shell import shell
from conjure import template
from conjure.utils import pollinate

from bundleplacer.config import Config
from bundleplacer.maas import connect_to_maas
from bundleplacer.placerview import PlacerView
from bundleplacer.controller import PlacementController, BundleWriter

from urllib.parse import urlparse
import os.path as path


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
        pollinate(self.app.session_id, 'PC')
        self.app.controllers['deploysummary'].render(self.bundle)

    def render(self, model):
        self.app.current_model = model
        info = model_info(self.app.current_model)
        # Grab bundle and deploy or render placement if MAAS
        self.bundle = get_bundle(BundleModel.to_entity(), to_file=True)
        metadata_filename = self.app.config['metadata_filename']

        bundleplacer_cfg = Config(
            'bundle-placer',
            {'bundle_filename': self.bundle,
             'metadata_filename': metadata_filename,
             'config_filename': self.app.argv.build_conf,
             'bundle_key': BundleModel.key()})

        if info['ProviderType'] == 'maas':
            pollinate(self.app.session_id, 'PM')
            bootstrap_config = model_cache_controller_provider(
                info['ServerUUID'])
            maas_server = urlparse(bootstrap_config['maas-server'])
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
            pollinate(self.app.session_id, 'PS')
            # TODO: cleanup a bit
            # FIXME: needs refinement.
            if info['ProviderType'] == 'lxd':
                # Process LXD pre setup scripts
                topdir = path.join('/usr/share', self.app.config['name'])
                lxd_profile = path.join(topdir, 'lxd-profile.yaml')
                pre_sh = path.join(topdir, 'lxd.sh')
                if path.isfile(pre_sh):
                    if path.isfile(lxd_profile):
                        tpl = template.load('lxd-profile.yaml', topdir)
                        out_tpl = template.save(
                            tpl, {'lxd_profile': "juju-{}".format(
                                info['Name'])})
                        cmd = ("bash {script} \"juju-{name}\" "
                               "\"{filepath}\"".format(
                                   name=info['Name'],
                                   filepath=out_tpl,
                                   script=pre_sh
                               ))
                        shell(cmd)
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
