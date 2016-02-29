from conjure.ui.views.welcome import WelcomeView
from conjure.models import CharmModel
from conjure.controllers.cloud import CloudController
from conjure.controllers.jujucontroller import JujuControllerController
from conjure.juju import Juju


class WelcomeController:
    def __init__(self, common):
        self.common = common
        self.view = WelcomeView(self.common, self.finish)

    def finish(self, name):
        """ Finalizes welcome controller

        Arguments:
        name: name of charm/bundle to use
        """
        deploy_key = next((n for n in
                           self.common['config']['bundles']
                           if n["name"] == name), None)

        if deploy_key is None:
            raise Exception(
                "Unable to determine bundle to deploy: {}".format(name))

        CharmModel.bundle = deploy_key
        if Juju.controllers() is None:
            CloudController(self.common, Juju.clouds().keys()).render()
        else:
            JujuControllerController(self.common).render()

    def render(self):
        config = self.common['config']
        self.common['ui'].set_header(
            title=config['summary'],
            excerpt=config['excerpt'],
        )
        self.common['ui'].set_body(self.view)
