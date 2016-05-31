from conjure import controllers
from conjure import utils
from conjure.api.models import model_info
from conjure import juju
from conjure.app_config import app
from subprocess import run, PIPE
import json
import os
import sys
import petname


this = sys.modules[__name__]
this.cloud = None


def do_post_bootstrap():
    """ runs post bootstrap script if exists
    """
    # Set provider type for post-bootstrap
    app.env['JUJU_PROVIDERTYPE'] = model_info('default')['ProviderType']

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


def finish():
    return controllers.use('variants').render()


def render(cloud):

    this.cloud = cloud
    if app.current_controller is None:
        app.current_controller = petname.Name()

    if app.current_model is None:
        app.current_model = 'default'

    juju.bootstrap(controller=app.current_controller,
                   cloud=this.cloud,
                   credential=None)
    do_post_bootstrap()
    finish()
