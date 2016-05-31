from conjure import controllers
from conjure import juju
from conjure import utils
from conjure.app_config import app
from subprocess import run, PIPE
import json
import os
import petname
import sys


def finish():
    controllers.use('deploy').render()


def render(cloud):
    if app.argv.cloud == "localhost":
        if not utils.check_bridge_exists():
            back = "{} to localhost".format(app.argv.config['spell'])
            os.execl("/usr/share/conjure-up/run-lxd-config",
                     "/usr/share/conjure-up/run-lxd-config",
                     back)

    if not juju.available():
        utils.info("Creating environment, please wait.")
        app.current_controller = petname.Name()
        juju.bootstrap(controller=app.current_controller,
                       cloud=cloud)
        juju.switch(app.current_controller)
    else:
        app.current_controller = juju.get_current_controller()

    post_bootstrap_sh = os.path.join(app.config['spell-dir'],
                                     'steps/00_post-bootstrap.sh')
    if os.path.isfile(post_bootstrap_sh) \
       and os.access(post_bootstrap_sh, os.X_OK):
        utils.pollinate(app.session_id, 'J001')
        utils.info("Running additional environment tasks.")
        try:
            sh = run(post_bootstrap_sh, shell=True, stdout=PIPE, stderr=PIPE)
            result = json.loads(sh.output.decode('utf8'))
            utils.info("Finished post bootstrap task: {}".format(
                result['message']))
        except Exception as e:
            utils.warning(
                "Failed to run post bootstrap task: {}".format(e))
            sys.exit(1)
    finish()
