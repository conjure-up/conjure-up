from conjure.ui.views.cloud import CloudView
from conjure.controllers.deploy import DeployController
from conjure.controllers.jujumodels.maas import MaasJujuModelController
from conjure.controllers.jujumodels.openstack import OpenStackJujuModelController  # noqa
from conjure.controllers.jujumodels.local import LocalJujuModelController
from conjure.juju import Juju


class CloudController:
    def __init__(self, common):
        self.common = common
        self.config = self.common['config']
        self.excerpt = (
            "Please select from a list of available clouds. "
            "This would be the equivalent of running `juju list-clouds`.\n\n"
            "For more information type `{cmd}` at your "
            "command prompt.".format(cmd='juju help list-clouds'))
        self.view = CloudView(self.common,
                              self.deploy)

    def deploy(self, model):
        """ An existing Juju model was found load the deploy controller
        to start installation

        Arguments:
        model: Juju model to deploy to
        """
        Juju.switch(model)
        DeployController(self.common, model).render()

    def render_model_view(self, model):
        """ No juju model found, render the selected models view
        for a new installation.

        Arguments:
        modmel: name of juju model to use
        """
        model = model.lower()
        if model == "maas":
            MaasJujuModelController(self.common).render()
        elif model == "openstack":
            OpenStackJujuModelController(self.common).render()
        elif model == "local":
            LocalJujuModelController(self.common).render()

    def render(self):
        self.common['ui'].set_header(
            title="Select a Juju Model",
            excerpt=self.excerpt
        )
        self.common['ui'].set_body(self.view)
