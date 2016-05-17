from bundleplacer.charmstore_api import MetadataController
from bundleplacer.config import Config
from bundleplacer.controller import PlacementController, BundleWriter
from conjure import controllers
from conjure.api.models import model_info
from conjure.app_config import app
from conjure.charm import get_bundle
from conjure.models.bundle import BundleModel
from conjure.ui.views.service_walkthrough import ServiceWalkthroughView
from conjure.utils import pollinate
import sys

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
        return controllers.use('jujucontroller')

    bw = BundleWriter(this.placement_controller)
    bw.write_bundle(this.bundle_filename)
    pollinate(app.session_id, 'PC')
    controllers.use('deploysummary').render(this.bundle_filename)


def render(model):
    app.current_model = model
    info = model_info(app.current_model)

    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']

    # Grab bundle and deploy or render placement if MAAS
    try:
        this.bundle_filename = get_bundle(BundleModel.to_entity(),
                                          to_file=True)
    except Exception as e:
        return app.ui.show_exception_message(e)

    metadata_filename = app.config['metadata_filename']
    config_filename = app.config['config_filename']

    bundleplacer_cfg = Config(
        'bundle-placer',
        {'bundle_filename': this.bundle_filename,
         'metadata_filename': metadata_filename,
         'config_filename': config_filename,
         'bundle_key': BundleModel.key(),
         'provider_type': info['ProviderType']})

    this.placement_controller = PlacementController(
        maas_state=None,
        config=bundleplacer_cfg)

    app.metadata_controller = MetadataController(
        this.placement_controller, bundleplacer_cfg)

    this.walkthrough_view = ServiceWalkthroughView(
        app, this.placement_controller)

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
