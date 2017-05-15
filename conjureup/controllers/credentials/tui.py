from conjureup import events, utils
from conjureup.app_config import app

from . import common


class CredentialsController(common.BaseController):
    def render(self):
        if app.current_cloud_type == 'localhost':
            # no credentials required for localhost
            self.finish(None)
        elif not self.creds:
            utils.warning("You attempted to do an install against a cloud "
                          "that requires credentials that could not be "
                          "found.  If you wish to supply those "
                          "credentials please run "
                          "`juju add-credential "
                          "{}`.".format(app.current_cloud))
            events.Shutdown.set(1)
        elif not self.default_credential:
            utils.warning("You attempted to install against a cloud with "
                          "multiple credentials and no default credentials "
                          "set.  Please set a default credential with:\n"
                          "\n"
                          "    juju set-default-credential {} <credential>")
            events.Shutdown.set(1)
        else:
            self.finish(self.default_credential)


_controller_class = CredentialsController
