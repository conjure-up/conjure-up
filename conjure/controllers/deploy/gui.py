import sys
from operator import attrgetter
import os.path as path


from bundleplacer.charmstore_api import MetadataController
from bundleplacer.config import Config
from bundleplacer.bundle import Bundle
from conjure import controllers
from conjure.app_config import app
from conjure.ui.views.service_walkthrough import ServiceWalkthroughView
from conjure.utils import pollinate

this = sys.modules[__name__]
this.bundle_filename = None
this.bundle = None
this.svc_idx = 0


def finish(service=None):
    """handles deployment

    Arguments:
    service: a dict for the service that was just configured. finish
    will deploy it and call render() again to display the next one.

    if service is None, continues to next controller

    """
    if service:
        # TODO do deploy of service
        this.svc_idx += 1
        return render()
    else:
        return controllers.use('deploystatus').render()

    pollinate(app.session_id, 'PC')


def render():
    this.bundle_filename = path.join(app.config['spell-dir'], 'bundle.yaml')

    bundleplacer_cfg = Config(
        'bundle-placer',
        {
            'bundle_filename': this.bundle_filename,
            'bundle_key': None,
        })

    if not this.bundle:
        this.bundle = Bundle(filename=this.bundle_filename)

    if not app.metadata_controller:
        app.metadata_controller = MetadataController(this.bundle,
                                                     bundleplacer_cfg)
    n_total = len(this.bundle.services)
    if this.svc_idx >= n_total:
        finish(service=None)
        return
    services = sorted(this.bundle.services, key=attrgetter('service_name'))
    service = services[this.svc_idx]

    wv = ServiceWalkthroughView(service, this.svc_idx, n_total,
                                app.metadata_controller, finish)

    app.ui.set_header("Review and Configure Applications")
    app.ui.set_body(wv)
