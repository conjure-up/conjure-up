from conjureup import events, utils
from conjureup.app_config import app

from . import common


class CredentialsController(common.BaseCredentialsController):
    def render(self):
        if app.provider.cloud_type == 'localhost':
            # no credentials required for localhost
            self.finish()
        elif not self.credentials:
            utils.warning("You attempted to do an install against a cloud "
                          "that requires credentials that could not be "
                          "found.  If you wish to supply those "
                          "credentials please run "
                          "`juju add-credential "
                          "{}`.".format(app.provider.cloud))
            events.Shutdown.set(1)
        elif not app.provider.credential:
            utils.warning("You attempted to install against a cloud with "
                          "multiple credentials and no default credentials "
                          "set.  Please set a default credential with:\n"
                          "\n"
                          "    juju set-default-credential {} <credential>")
            events.Shutdown.set(1)
        else:
            self.finish()


_controller_class = CredentialsController
