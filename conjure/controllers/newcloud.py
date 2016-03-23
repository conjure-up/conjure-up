from conjure.ui.views.newcloud import NewCloudView
from conjure.models.provider import Schema


class NewCloudController:
    """ Renders an input view for defining selected clouds credentials
    """

    def __init__(self, app):
        self.app = app

    def finish(self, credentials=None, back=False):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        credentials: credentials to store for provider
        back: if true loads previous controller
        """
        if back:
            return self.app.controllers['clouds'].render()

        self.app.controllers['jujucontroller'].render(
            credentials, bootstrap=True)

    def render(self, cloud):
        """ Render

        Arguments:
        cloud: The cloud to create credentials for
        """
        # if cloud is LXD bypass all this
        if cloud == 'lxd':
            return self.app.controllers['jujucontroller'].render(
                bootstrap=True)

        try:
            creds = Schema[cloud]
        except KeyError as e:
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
