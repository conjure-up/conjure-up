from conjure import async
from conjure import juju
from conjure.app_config import app
from conjure.models.bundle import BundleModel
from conjure.ui.views.jujucontroller import JujuControllerView
from conjure import utils
from conjure import controllers
from functools import partial
from subprocess import check_output
from ubuntui.ev import EventLoop
import json
import os
import os.path as path
import petname
import sys

this = sys.modules[__name__]
this.cloud = None
this.bootstrap = None
this._post_bootstrap_pollinate = False


def __handle_exception(exc):
    utils.pollinate(app.session_id, 'EB')
    return app.ui.show_exception_message(exc)


def __handle_bootstrap_done(future):
    app.log.debug("handle bootstrap")
    result = future.result()
    if result.code > 0:
        app.log.error(result.errors())
        return __handle_exception(Exception(result.errors()))
    utils.pollinate(app.session_id, 'J004')
    EventLoop.remove_alarms()
    juju.switch(app.current_controller)
    __post_bootstrap_exec()


def __post_bootstrap_exec():
    """ Executes post-bootstrap.sh if exists
    """
    _post_bootstrap_sh = path.join(app.config['metadata']['spell-dir'],
                                   'scripts/post-bootstrap.sh')
    if path.isfile(_post_bootstrap_sh) \
       and os.access(_post_bootstrap_sh, os.X_OK):
        app.ui.set_footer('Running post-bootstrap tasks.')
        utils.pollinate(app.session_id, 'J001')
        app.log.debug("post_bootstrap running: {}".format(
            _post_bootstrap_sh
        ))
        try:
            future = async.submit(partial(check_output,
                                          _post_bootstrap_sh,
                                          shell=True,
                                          env=app.env),
                                  __handle_exception)
            future.add_done_callback(__post_bootstrap_done)
        except Exception as e:
            return __handle_exception(e)


def __post_bootstrap_done(future):
    try:
        result = json.loads(future.result().decode('utf8'))
    except Exception as e:
        return __handle_exception(e)

    app.log.debug("post_bootstrap_done: {}".format(result))
    if result['returnCode'] > 0:
        utils.pollinate(app.session_id, 'E001')
        return __handle_exception(Exception(
            'There was an error during the post '
            'bootstrap processing phase: {}.'.format(result)))
    utils.pollinate(app.session_id, 'J002')
    app.log.debug("Switching to controller: {}".format(
        app.current_controller))
    juju.switch(app.current_controller)
    controllers.use('deploy').render(app.current_controller)


def finish(controller=None, back=False):
    """ Deploy to juju controller

    Arguments:
    controller: Juju controller to deploy to
    back: if true returns to previous controller
    """
    app.log.debug(
        "jujucontroller - selected: {}".format(controller))
    app.current_controller = controller

    if back:
        return controllers.use('clouds').render()

    if this.bootstrap:
        app.log.debug("Performing bootstrap: {} {}".format(
            controller, this.cloud))
        future = juju.bootstrap_async(
            controller=app.current_controller,
            cloud=this.cloud,
            series=BundleModel.bootstrapSeries(),
            exc_cb=__handle_exception,
            log=app.log)
        future.add_done_callback(
            __handle_bootstrap_done)

        controllers.use('bootstrapwait').render()
        utils.pollinate(app.session_id, 'J003')

    else:
        controllers.use('deploy').render(app.current_controller)


def render(cloud=None, bootstrap=None):
    """ Render controller

    Arguments:
    cloud: defined cloud to use when deploying
    bootstrap: is this a new environment that needs to be bootstrapped
    """

    this.cloud = cloud

    # Set provider type for post-bootstrap
    app.env['JUJU_PROVIDERTYPE'] = this.cloud

    bootstrap = bootstrap

    if this.cloud and bootstrap:
        if app.current_controller is not None:
            return finish(app.current_controller)
        else:
            app.current_controller = petname.Name()
            return finish(app.current_controller)
        return __handle_exception(Exception(
            "Unable to determine a controller to bootstrap"))

    controllers = juju.get_controllers().keys()
    models = {}
    for c in controllers:
        juju.switch(c)
        models[c] = juju.get_models()
    view = JujuControllerView(app,
                              models,
                              finish)

    app.ui.set_header(
        title="Juju Model",
    )
    app.ui.set_body(view)
