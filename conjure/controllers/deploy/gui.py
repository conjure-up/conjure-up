from concurrent import futures
from functools import partial

import sys

from ubuntui.ev import EventLoop

from conjure import controllers
from conjure import juju
from conjure.app_config import app
from conjure.ui.views.service_walkthrough import ServiceWalkthroughView
from conjure import utils

from .common import get_bundleinfo, get_metadata_controller

this = sys.modules[__name__]
this.bundle_filename = None
this.bundle = None
this.services = []
this.svc_idx = 0
this.showing_error = False


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    app.ui.show_exception_message(exc)
    this.showing_error = True
    EventLoop.remove_alarms()


def finish(single_service=None):
    """handles deployment

    Arguments:

    single_service: a dict for the service that was just
    configured. finish will schedule a deploy for it and
    call render() again to display the next one.

    if service is None, schedules deploys for all remaining services,
    schedules relations, then continues to next controller

    """
    if single_service:
        juju.deploy_service(single_service,
                            app.ui.set_footer,
                            partial(__handle_exception, "ED"))
        this.svc_idx += 1
        return render()
    else:
        for service in this.services[this.svc_idx:]:
            juju.deploy_service(service,
                                app.ui.set_footer,
                                partial(__handle_exception, "ED"))

        f =juju.set_relations(this.services,
                              app.ui.set_footer,
                              partial(__handle_exception, "ED"))

        return controllers.use('deploystatus').render(f)

    utils.pollinate(app.session_id, 'PC')


def render():
    if this.showing_error:
        return
    if not this.bundle:
        this.bundle_filename, this.bundle, this.services = get_bundleinfo()

    if not app.metadata_controller:
        app.metadata_controller = get_metadata_controller(this.bundle,
                                                          this.bundle_filename)

    n_total = len(this.bundle.services)
    if this.svc_idx >= n_total:
        return finish(single_service=None)

    service = this.services[this.svc_idx]
    wv = ServiceWalkthroughView(service, this.svc_idx, n_total,
                                app.metadata_controller, finish)

    app.ui.set_header("Review and Configure Applications")
    app.ui.set_body(wv)
