from conjure.ui.views import (NewModelView, ExistingModelView)
from conjure.controllers.deploy import DeployController
from .jujumodels import (MaasModelController,
                         OpenStackModelController,
                         LocalModelController)


class JujuModelController:
    def __init__(self, common, jujumodels=None):
        self.common = common
        self.jujumodels = jujumodels
        if self.jujumodels is None:
            self.view = NewModelView(self.common,
                                     self.render_model_view)
        else:
            self.view = ExistingModelView(self.common,
                                          self.jujumodels,
                                          self.deploy)

    def deploy(self, model):
        """ An existing Juju model was found load the deploy controller
        to start installation

        Arguments:
        model: Juju model to deploy to
        """
        self.common['juju'].switch(model)
        model_info = self.common['juju'].client.Client(request="ModelInfo")
        DeployController(self.common, model_info['name']).render()

    def render_model_view(self, model):
        """ No juju model found, render the selected models view
        for a new installation.

        Arguments:
        modmel: name of juju model to use
        """
        model = model.lower()
        if model == "maas":
            MaasModelController(self.common).render()
        elif model == "openstack":
            OpenStackModelController(self.common).render()
        elif model == "local":
            LocalModelController(self.common).render()

    def render(self):
        self.common['ui'].set_header(
            title="Select a Juju Model",
            excerpt="A Juju environment is required to deploy the solution. "
            "Since no existing environments were found please "
            "select the model you wish to use."
        )
        self.common['ui'].set_body(self.view)
