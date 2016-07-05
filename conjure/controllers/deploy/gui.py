from functools import partial
import json
import sys
import os
from ubuntui.ev import EventLoop
from subprocess import run, PIPE
from conjure import controllers
from conjure import juju
from conjure import async
from conjure.app_config import app
from conjure.ui.views.service_walkthrough import ServiceWalkthroughView
from conjure import utils
from conjure.api.models import model_info
from .common import get_bundleinfo, get_metadata_controller

this = sys.modules[__name__]
this.bundle_filename = None
this.bundle = None
this.services = []
this.svc_idx = 0
this.showing_error = False
this.is_predeploy_queued = False


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    app.ui.show_exception_message(exc)
    this.showing_error = True
    EventLoop.remove_alarms()


def __pre_deploy_exec():
    """ runs pre deploy script if exists
    """
    this.is_predeploy_queued = True
    app.env['JUJU_PROVIDERTYPE'] = model_info(
        juju.get_current_model())['provider-type']

    pre_deploy_sh = os.path.join(app.config['spell-dir'],
                                 'conjure/steps/00_pre-deploy')
    if os.path.isfile(pre_deploy_sh) \
       and os.access(pre_deploy_sh, os.X_OK):
        utils.pollinate(app.session_id, 'J001')
        msg = "Running pre-deployment tasks."
        app.log.debug(msg)
        app.ui.set_footer(msg)
        return run(pre_deploy_sh,
                   shell=True,
                   stdout=PIPE,
                   stderr=PIPE,
                   env=app.env)
    return json.dumps({'message': 'No pre deploy necessary',
                       'returnCode': 0,
                       'isComplete': True})


def __pre_deploy_done(future):
    try:
        result = json.loads(future.result().stdout.decode())
    except AttributeError:
        result = json.loads(future.result())
    except:
        return __handle_exception(
            'E003',
            Exception(
                "Problem with pre-deploy: \n{}, ".format(
                    future.result())))

    app.log.debug("pre_deploy_done: {}".format(result))
    if result['returnCode'] > 0:
        utils.pollinate(app.session_id, 'E003')
        return __handle_exception('E003', Exception(
            'There was an error during the pre '
            'deploy processing phase: {}.'.format(result)))
    else:
        app.ui.set_footer("Pre-deploy processing done.")


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

        f = juju.set_relations(this.services,
                               app.ui.set_footer,
                               partial(__handle_exception, "ED"))

        return controllers.use('deploystatus').render(f)

    utils.pollinate(app.session_id, 'PC')


def render():
    if not this.is_predeploy_queued:
        try:
            future = async.submit(__pre_deploy_exec,
                                  partial(__handle_exception, 'E003'),
                                  queue_name=juju.JUJU_ASYNC_QUEUE)
            future.add_done_callback(__pre_deploy_done)
        except Exception as e:
            return __handle_exception('E003', e)

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
