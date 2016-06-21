from conjure.ui.views.deploystatus import DeployStatusView
from ubuntui.ev import EventLoop
from conjure.app_config import app
from conjure import utils
from conjure import controllers
from conjure import async
from functools import partial
from . import common
import os.path as path
import os
import sys


this = sys.modules[__name__]
this.view = None
this.pre_exec_pollinate = False
this.bundle = path.join(
    app.config['spell-dir'], 'bundle.yaml')
this.bundle_scripts = path.join(
    app.config['spell-dir'], 'conjure/steps'
)


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    return app.ui.show_exception_message(exc)


def __wait_for_applications(*args):
    deploy_done_sh = os.path.join(this.bundle_scripts,
                                  '00_deploy-done')

    future = async.submit(partial(common.wait_for_applications,
                                  deploy_done_sh,
                                  app.ui.set_footer),
                          partial(__handle_exception, 'ED'))
    future.add_done_callback(finish)


def finish(future):
    if not future.exception():
        return controllers.use('steps').render()
    EventLoop.remove_alarms()


def __refresh(*args):
    this.view.refresh_nodes()
    EventLoop.set_alarm_in(1, __refresh)


def render(deploy_future):
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
    deploy_future.add_done_callback(__refresh)
    deploy_future.add_done_callback(__wait_for_applications)
