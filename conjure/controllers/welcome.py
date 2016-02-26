from conjure.ui.views.welcome import WelcomeView
from conjure.models import CharmModel
from conjure.controllers.jujumodel import JujuModelController
from conjure.juju import Juju
from ubuntui.ev import EventLoop


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

        if not Juju.available():
            self.common['ui'].show_error_message(
                "For now, initialize a juju model.")
            EventLoop.remove_alarms()
        else:
            JujuModelController(self.common, Juju.clouds().keys()).render()

    def render(self):
        config = self.common['config']
        self.common['ui'].set_header(
            title=config['summary'],
            excerpt=config['excerpt'],
        )
        self.common['ui'].set_body(self.view)
