from conjure.ui.views.jujumodel import (NewModelView, ExistingModelView)
from conjure.controllers.deploy import DeployController
from conjure.controllers.jujumodels import (MaasJujuModelController,
                                            OpenStackJujuModelController,
                                            LocalJujuModelController)


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
        if model_info['ProviderType'] in self.common['juju-models']:
            model = self.common['juju-models'][model_info['ProviderType']]
            model.name = model_info['Name']
            model.provider_type = model_info['ProviderType']
            DeployController(self.common, model).render()
        else:
            raise Exception("Unknown Provider Type found: {}".format(
                model_info['ProviderType']
            ))

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
            excerpt="A Juju environment is required to deploy the solution. "
            "Since no existing environments were found please "
            "select the model you wish to use."
        )
        self.common['ui'].set_body(self.view)
