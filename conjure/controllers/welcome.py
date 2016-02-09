from conjure.ui.views import WelcomeView
from conjure.models import CharmModel
from conjure.controllers.jujumodel import JujuModelController


class WelcomeController:
    def __init__(self, common):
        self.common = common
        self.juju = self.common['juju']
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

        if self.juju.available():
            self.juju.login()
            models = self.juju.list_models()
            JujuModelController(self.common, models).render()
        else:
            JujuModelController(self.common, None).render()

    def render(self):
        config = self.common['config']
        self.common['ui'].set_header(
            title=config['summary'],
            excerpt=config['excerpt'],
        )
        self.common['ui'].set_footer("(Q)uit")
        self.common['ui'].set_body(self.view)
