from conjure.ui.views.newcloud import NewCloudView
from conjure.models.provider import Schema
from conjure.utils import juju_path, pollinate
from configobj import ConfigObj
import os.path as path
import yaml
import petname


class NewCloudController:
    """ Renders an input view for defining selected clouds credentials
    """

    def __init__(self, app):
        self.app = app

    def _format_creds(self, creds):
        """ Formats the credentials into strings from the widgets values
        """
        formatted = {}
        for k, v in creds.items():
            if k.startswith('_'):
                # Not a widget but a private key
                k = k[1:]
                formatted[k] = v
            elif k.startswith('@'):
                # A Widget, but not stored in credentials
                continue
            else:
                formatted[k] = v.value
        return formatted

    def finish(self, credentials=None, back=False):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        credentials: credentials to store for provider
        back: if true loads previous controller
        """
        self.app.current_controller = petname.Name()

        if back:
            return self.app.controllers['welcome'].render()

        cred_path = path.join(juju_path(), 'credentials.yaml')
        if not path.isfile(cred_path):
            existing_creds = {
                    'credentials': {
                        self.cloud: {
                            self.app.current_controller: self._format_creds(
                                credentials)
                        }
                    }
                }

        else:
            existing_creds = yaml.safe_load(open(cred_path))

            if self.cloud in existing_creds['credentials'].keys():
                c = existing_creds['credentials'][self.cloud]
                c[self.app.current_controller] = self._format_creds(
                    credentials)
            else:
                # Handle the case where path exists but an entry for the cloud
                # has yet to be added.
                existing_creds['credentials'][self.cloud] = {
                    self.app.current_controller: self._format_creds(
                        credentials)
                }

        with open(cred_path, 'w') as cred_f:
            cred_f.write(yaml.safe_dump(existing_creds,
                                        default_flow_style=False))

        if self.cloud == 'maas':
            self.cloud = '{}/{}'.format(self.cloud,
                                        credentials['@maas-server'].value)
        pollinate(self.app.session_id, 'CA', self.app.log)
        self.app.controllers['jujucontroller'].render(
            self.cloud, bootstrap=True)

    def render(self, cloud):
        """ Render

        Arguments:
        cloud: The cloud to create credentials for
        """

        # LXD is a special case as we want to make sure a bridge
        # is configured. If not we'll bring up a new view to allow
        # a user to configure a LXD bridge with suggested network
        # information.
        if cloud == 'lxd' or cloud == 'localhost':
            if path.isfile('/etc/default/lxd-bridge'):
                cfg = ConfigObj('/etc/default/lxd-bridge')
            else:
                cfg = ConfigObj()

            ready = cfg.get('LXD_IPV4_ADDR', None)
            if not ready:
                return self.app.controllers['lxdsetup'].render()

            self.app.log.debug("Found an IPv4 address ({}), "
                               "assuming LXD is configured.".format(ready))
            return self.app.controllers['jujucontroller'].render(
                cloud='lxd', bootstrap=True)

        try:
            creds = Schema[cloud]
        except KeyError as e:
            pollinate(self.app.session_id, 'EC', self.app.log)
            self.app.ui.show_exception_message(e)

        self.config = self.app.config
        self.cloud = cloud
        self.view = NewCloudView(self.app,
                                 self.cloud,
                                 creds,
                                 self.finish)

        self.app.ui.set_header(
            title="New cloud setup",
        )
        self.app.ui.set_body(self.view)
