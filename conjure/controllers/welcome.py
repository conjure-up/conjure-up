from conjure.ui.views.welcome import WelcomeView
from conjure.models.bundle import BundleModel
from conjure.juju import Juju


class WelcomeController:
    def __init__(self, app):
        self.app = app
        self.view = WelcomeView(self.app, self.finish)

    def finish(self, name):
        """ Finalizes welcome controller

        Arguments:
        name: name of charm/bundle to use
        """
        deploy_key = next((n for n in
                           self.app.config['bundles']
                           if n["name"] == name), None)

        if deploy_key is None:
            raise Exception(
                "Unable to determine bundle to deploy: {}".format(name))

        BundleModel.bundle = deploy_key
        if Juju.controllers() is None:
            self.app.controllers['clouds'](self.app).render()
        else:
            self.app.controllers['jujucontroller'](self.app).render()

    def render(self):
        config = self.app.config
        self.app.ui.set_header(
            title=config['summary'],
            excerpt=config['excerpt'],
        )
        self.app.ui.set_body(self.view)
