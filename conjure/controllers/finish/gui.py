from conjure.ui.views.services import ServicesView
from ubuntui.ev import EventLoop
from conjure import juju
from functools import partial
from conjure import async
from conjure.app_config import app
from conjure.models.bundle import BundleModel
from conjure import utils
import os.path as path
import os
import json
import sys
from subprocess import run, PIPE


this = sys.modules[__name__]
this.post_exec_pollinate = False
this.pre_exec_pollinate = False
this.bundle = None


def finish():
    pass


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    app.ui.show_exception_message(exc)


def __handle_post_exception(exc):
    """ If an exception occurs in the post processing,
    log it but don't die
    """
    utils.pollinate(app.session_id, 'E002')
    app.log.exception(exc)


def __handle_pre_exception(exc):
    """ If an exception occurs in the pre processing,
    log it but don't die
    """
    utils.pollinate(app.session_id, 'E003')
    app.ui.show_exception_message(exc)


def __pre_exec(*args):
    """ Executes a bundles pre processing script if exists
    """
    app.log.debug("pre_exec start: {}".format(args))

    try:
        bundle_key = app.cache['selected_bundle']['key']
    except:
        bundle_key = BundleModel.key()

    _pre_exec_sh = path.join('/usr/share/',
                             app.config['name'],
                             'bundles',
                             bundle_key,
                             'pre.sh')
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
        future = async.submit(partial(run,
                                      _pre_exec_sh,
                                      shell=True,
                                      stderr=PIPE,
                                      stdout=PIPE,
                                      env=app.env),
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
    app.log.debug("Deploying bundle: {}".format(this.bundle))
    app.ui.set_footer('Deploying bundle...')
    utils.pollinate(app.session_id, 'DS')
    future = async.submit(
        partial(juju.deploy_bundle, this.bundle),
        partial(__handle_exception, "ED"))
    future.add_done_callback(__deploy_bundle_done)


def __deploy_bundle_done(future):
    result = future.result()
    app.log.debug("deploy_bundle_done: {}".format(result.output()))
    if result.code > 0:
        __handle_exception("ED", Exception(
            'There was an error deploying the bundle: {}.'.format(
                result.errors())))
        return
    app.ui.set_footer('Deploy committed, waiting...')
    utils.pollinate(app.session_id, 'DC')
    EventLoop.set_alarm_in(1, __post_exec)


def __post_exec(*args):
    """ Executes a bundles post processing script if exists
    """
    try:
        bundle_key = app.cache['selected_bundle']['key']
    except:
        bundle_key = BundleModel.key()
        if bundle_key is None:
            app.log.debug(
                "Could not determine bundle used, skipping post_exec")
            EventLoop.set_alarm_in(1, __refresh)
            return
    _post_exec_sh = path.join('/usr/share/',
                              app.config['name'],
                              'bundles',
                              bundle_key,
                              'post.sh')

    if not path.isfile(_post_exec_sh) \
       or not os.access(_post_exec_sh, os.X_OK):
        app.log.debug(
            "Unable to execute: {}, skipping".format(_post_exec_sh))
        return

    if not this.post_exec_pollinate:
        # We dont want to keep pollinating since this routine could
        # run multiple times
        utils.pollinate(app.session_id, 'XB')
        this.post_exec_pollinate = True

    app.log.debug("post_exec running: {}".format(_post_exec_sh))
    future = async.submit(partial(run,
                                  _post_exec_sh,
                                  shell=True,
                                  stderr=PIPE,
                                  stdout=PIPE,
                                  env=app.env),
                          __handle_post_exception)
    future.add_done_callback(__post_exec_done)


def __post_exec_done(future):
    try:
        fr = future.result()
        try:
            result = json.loads(fr.stdout.decode())
        except json.decoder.JSONDecodeError:
            result = dict(returnCode=1, fr=fr,
                          jsonError=True,
                          message="Retrying post-processing.")

        app.log.debug("post_exec_done: {}".format(result))
        app.log.warning(fr.stderr.decode())
        app.ui.set_footer(result['message'])
        if result['returnCode'] > 0 or not result['isComplete']:
            app.log.error(
                'There was an error during the post processing '
                'phase, retrying.')
            EventLoop.set_alarm_in(5, __post_exec)
        else:
            # Stop post processing loop and restart view refresh
            EventLoop.remove_alarms()
            EventLoop.set_alarm_in(1, __refresh)
    except Exception as e:
        app.log.error(e)
        __handle_exception("E002", e)


def __refresh(*args):
    this.view.refresh_nodes()
    EventLoop.set_alarm_in(1, __refresh)


def render(bundle):
    """ Render services status view

    Arguments:
    bundle: modified bundle to deploy
    """
    this.bundle = bundle
    view = ServicesView(app)

    app.ui.set_header(
        title="Conjuring up {} thanks to Juju".format(
            app.config['spell'])
    )
    app.ui.set_body(view)
    app.ui.set_subheader(
        'Deploy Status - (Q)uit || UP/DOWN to Scroll')

    if not app.argv.status_only:
        app.log.debug("No --status-only pass, running pre_exec")
        EventLoop.set_alarm_in(1, __pre_exec)
    else:
        # Re-run post processor if loading the status screen
        EventLoop.set_alarm_in(1, __post_exec)
        app.ui.set_footer('')
    EventLoop.set_alarm_in(1, __refresh)
