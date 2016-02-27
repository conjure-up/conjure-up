from conjure.ui.views.jujucontroller import JujuControllerView
from conjure.controllers.deploy import DeployController
from conjure.juju import Juju


class JujuControllerController:
    def __init__(self, common, cloud):
        self.common = common
        self.cloud = cloud
        self.controllers = Juju.controllers()
        self.config = self.common['config']
        if self.controllers is None:
            self.excerpt = (
                "A Juju controller is required to deploy the solution. "
                "Since no existing controllers were found please "
                "type a name to create a new controller.")

            self.view = JujuControllerView(self.common,
                                           None,
                                           self.deploy)
        else:
            self.excerpt = (
                "It looks like there are existing Juju controllers, "
                "please select the controller you wish to deploy to or "
                "enter a new name to create a new controller.")
            self.view = JujuControllerView(self.common,
                                           self.controllers,
                                           self.deploy)

    def deploy(self, controller, existing=True):
        """ Deploy to juju controller

        Arguments:
        controller: Juju controller to deploy to
        existing: is the controller new or not
        """
        DeployController(self.common, controller, existing).render()

    def render(self):
        self.common['ui'].set_header(
            title="Juju Controller",
            excerpt=self.excerpt
        )
        self.common['ui'].set_body(self.view)
