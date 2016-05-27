from bundleplacer.charmstore_api import MetadataController
from bundleplacer.config import Config
from bundleplacer.controller import PlacementController, BundleWriter
from conjure import controllers
from conjure.app_config import app
from conjure.ui.views.service_walkthrough import ServiceWalkthroughView
from conjure.utils import pollinate
import sys
import os.path as path

this = sys.modules[__name__]
this.placement_controller = None
this.bundle_filename = None
this.walkthrough_view = None


def finish(back=False):
    """ handles deployment

    Arguments:
    back: if true returns to previous controller
    """
    if back:
        return controllers.use('jujucontroller').render()

    bw = BundleWriter(this.placement_controller)
    bw.write_bundle(this.bundle_filename)
    pollinate(app.session_id, 'PC')


def render(controller):

    bundleplacer_cfg = Config(
        'bundle-placer',
        {
            'bundle_filename': path.join(app.config['spell-dir'],
                                         'bundle.yaml'),
            # 'metadata_filename': metadata_filename,
            'bundle_key': None,
            # 'provider_type': info['ProviderType']
        })

    this.placement_controller = PlacementController(
        maas_state=None,
        config=bundleplacer_cfg)

    app.metadata_controller = MetadataController(
        this.placement_controller, bundleplacer_cfg)

    this.walkthrough_view = ServiceWalkthroughView(
        app, this, this.placement_controller)

    app.ui.set_subheader("Service Walkthrough")
    app.ui.set_body(this.walkthrough_view)
    this.walkthrough_view.update()


def __handle_service_scale_change(service, value):
    ""
    this.walkthrough_view.handle_service_scale_change(service, value)


def __handle_service_ctype_change(service, value):
    ""
    this.walkthrough_view.handle_service_ctype_change(service, value)


def __handle_service_deploy(service):
    "TODO: deploy one at a time eventually"
    this.walkthrough_view.handle_service_deploy(service)
