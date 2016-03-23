from conjure.ui.views.newcloud import NewCloudView
from conjure.models.provider import Schema
from conjure.utils import Host, pollinate
import os.path as path
import yaml


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
            # Not a widget but a private key
            if k.startswith('_'):
                k = k[1:]
                formatted[k] = v
            else:
                formatted[k] = v.value
        return formatted

    def finish(self, credentials=None, back=False):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        credentials: credentials to store for provider
        back: if true loads previous controller
        """
        if back:
            return self.app.controllers['clouds'].render()

        cred_path = path.join(Host.juju_path(), 'credentials.yaml')
        if path.isfile(cred_path):
            existing_creds = yaml.safe_load(open(cred_path))

            if self.cloud in existing_creds['credentials'].keys():
                c = existing_creds['credentials'][self.cloud]
                c['conjure'] = self._format_creds(
                    credentials)
        else:
            existing_creds = {
                'credentials': {
                    self.cloud: {'conjure': self._format_creds(credentials)}
                }
            }
        with open(cred_path, 'w') as cred_f:
            cred_f.write(yaml.safe_dump(existing_creds,
                                        default_flow_style=False))

        # FIXME: Handle these cases better
        if self.cloud == 'maas':
            self.cloud = '{}/{}'.format(self.cloud,
                                        credentials['maas-server'].value)
        pollinate(self.app.session_id, 'CA')
        self.app.controllers['jujucontroller'].render(
            self.cloud, bootstrap=True)

    def render(self, cloud):
        """ Render

        Arguments:
        cloud: The cloud to create credentials for
        """
        # if cloud is LXD bypass all this
        if cloud == 'lxd':
            return self.app.controllers['jujucontroller'].render(
                cloud='lxd', bootstrap=True)

        try:
            creds = Schema[cloud]
        except KeyError as e:
            pollinate(self.app.session_id, 'EC')
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
