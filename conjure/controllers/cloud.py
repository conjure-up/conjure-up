from conjure.ui.views.cloud import CloudView
from conjure.juju import Juju
from conjure.utils import pollinate, info, warning
import sys


class TUI:
    def __init__(self, app):
        self.app = app

    def finish(self):
        self.app.log.debug("TUI finish")

    def render(self):
        if self.app.argv.cloud not in Juju.clouds().keys():
            warning("Unknown Cloud: {}".format(self.app.argv.cloud))
            sys.exit(1)
        info(
            "Deploying to: {}".format(self.app.argv.cloud))


class GUI:
    def __init__(self, app):
        self.app = app

    def _list_clouds(self):
        """ Returns list of clouds filtering out any results
        """
        clouds = set(Juju.clouds().keys())

        if 'cloud_whitelist' in self.app.config['metadata']:
            whitelist = set(self.app.config['metadata']['cloud_whitelist'])
            return sorted(list(clouds & whitelist))

        elif 'cloud_blacklist' in self.app.config['metadata']:
            blacklist = set(self.app.config['metadata']['cloud_blacklist'])
            return sorted(list(clouds ^ blacklist))

        return sorted(list(clouds))

    def finish(self, cloud=None, create_cloud=False, back=False):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        cloud: Cloud to create the controller/model on.
        create_cloud: True/False, if true display create cloud interface
        back: if true loads previous controller
        """
        if back:
            return self.app.controllers['welcome'].render()

        if create_cloud:
            return self.app.controllers['newcloud'].render(cloud)

        pollinate(self.app.session_id, 'CS', self.app.log)

    def render(self):
        self.clouds = self._list_clouds()
        self.config = self.app.config
        self.excerpt = ("Please select from a list of available clouds")
        self.view = CloudView(self.app,
                              self.clouds,
                              self.finish)

        self.app.ui.set_header(
            title="Cloud Providers",
            excerpt=self.excerpt
        )
        self.app.ui.set_body(self.view)


def load_cloud_controller(app):
    if app.headless:
        return TUI(app)
    else:
        return GUI(app)
