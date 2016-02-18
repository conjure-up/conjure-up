from conjure.ui.views.jujumodel import (NewModelView, ExistingModelView)
from conjure.controllers.deploy import DeployController
from conjure.controllers.jujumodels.maas import MaasJujuModelController
from conjure.controllers.jujumodels.openstack import OpenStackJujuModelController  # noqa
from conjure.controllers.jujumodels.local import LocalJujuModelController


class JujuModelController:
    def __init__(self, common, jujumodels=None):
        self.common = common
        self.config = self.common['config']
        self.jujumodels = jujumodels
        if self.jujumodels is None:
            self.excerpt = (
                "A Juju environment is required to deploy the solution. "
                "Since no existing environments were found please "
                "select the model you wish to use. This would be the "
                "equivalent of running `juju bootstrap -e <model>`.\n\n"
                "For more information type `{cmd}` at your "
                "command prompt.".format(cmd='juju help bootstrap'))

            self.view = NewModelView(self.common,
                                     self.render_model_view)
        else:
            self.excerpt = (
                "It looks like there are existing Juju Models, please select "
                "the model you wish to deploy to. This would be the "
                "equivalent of running `juju list-models`.\n\n"
                "For more information type `{cmd}` at your "
                "command prompt.".format(cmd='juju help controllers'))
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
