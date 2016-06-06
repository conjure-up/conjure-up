from conjure.ui.views.deploystatus import DeployStatusView
from ubuntui.ev import EventLoop
from conjure import juju
from functools import partial
from conjure import async
from conjure.app_config import app
from conjure import utils
from conjure import controllers
from conjure.api.models import model_info
from . import common
import os.path as path
import os
import json
import sys


this = sys.modules[__name__]
this.view = None
this.pre_exec_pollinate = False
this.bundle = path.join(
    app.config['spell-dir'], 'bundle.yaml')
this.bundle_scripts = path.join(
    app.config['spell-dir'], 'conjure/steps'
)


def __fatal(error):
    return __handle_exception('ED', Exception(error))


def finish():
    deploy_done_sh = os.path.join(this.bundle_scripts,
                                  '00_deploy-done.sh')
    common.wait_for_applications(deploy_done_sh,
                                 __fatal,
                                 app.ui.set_footer)
    return controllers.use('steps').render()


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    app.ui.show_exception_message(exc)


def __handle_pre_exception(exc):
    """ If an exception occurs in the pre processing,
    log it but don't die
    """
    utils.pollinate(app.session_id, 'E003')
    app.ui.show_exception_message(exc)


def __pre_exec(*args):
    """ Executes a bundles pre processing script if exists
    """
    info = model_info(app.current_model)
    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']
    app.env['CONJURE_SPELL'] = app.config['spell']
    app.log.debug(
        "pre_exec start: {}/provider-type:{}".format(
            app.env['CONJURE_SPELL'],
            app.env['JUJU_PROVIDERTYPE']))

    _pre_exec_sh = path.join(this.bundle_scripts, '00_pre.sh')
    if not path.isfile(_pre_exec_sh) \
       or not os.access(_pre_exec_sh, os.X_OK):
        app.log.debug(
            "Unable to execute: {}, skipping".format(_pre_exec_sh))
        return __deploy_bundle()
    app.ui.set_footer('Running pre-processing tasks...')
    if not this.pre_exec_pollinate:
        utils.pollinate(app.session_id, 'XA')
        this.pre_exec_pollinate = True

    app.log.debug("pre_exec running {}".format(_pre_exec_sh))

    try:
        future = async.submit(partial(common.run_script,
                                      _pre_exec_sh),
                              partial(__handle_exception,
                                      "E002"))
        future.add_done_callback(__pre_exec_done)
    except Exception as e:
        __handle_exception("E002", e)


def __pre_exec_done(future):
    fr = future.result()
    result = json.loads(fr.stdout.decode('utf8'))
    app.log.debug("pre_exec_done: {}".format(result))
    app.log.warning(fr.stderr.decode())
    if result['returnCode'] > 0:
        return __handle_pre_exception(Exception(
            'There was an error during the pre processing phase.'))
    __deploy_bundle()


def __deploy_bundle():
    """ Performs the bootstrap in between processing scripts
    """
    juju.switch(juju.get_current_model())
    app.log.debug("Deploying bundle: {}".format(this.bundle))
    app.ui.set_footer('Deploying bundle...')
    utils.pollinate(app.session_id, 'DS')
    future = async.submit(
        partial(juju.deploy, this.bundle),
        partial(__handle_exception, "ED"))
    future.add_done_callback(__deploy_bundle_done)


def __deploy_bundle_done(future):
    result = future.result()
    app.log.debug("deploy_bundle_done: {}".format(result))
    if result.returncode > 0:
        __handle_exception("ED", Exception(
            'There was an error deploying the bundle: {}.'.format(
                result.stderr.decode('utf8'))))
        return
    app.ui.set_footer('Deploy committed, waiting...')
    utils.pollinate(app.session_id, 'DC')
    finish()


def __refresh(*args):
    this.view.refresh_nodes()
    EventLoop.set_alarm_in(1, __refresh)


def render():
    """ Render deploy status view
    """
    this.view = DeployStatusView(app)

    try:
        name = app.config['metadata']['friendly-name']
    except KeyError:
        name = app.config['spell']
    app.ui.set_header(
        title="Conjuring up {}".format(
            name)
    )
    app.ui.set_body(this.view)
    EventLoop.set_alarm_in(1, __pre_exec)
    EventLoop.set_alarm_in(1, __refresh)
