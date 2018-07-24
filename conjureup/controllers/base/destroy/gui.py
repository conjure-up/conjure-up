import os
import json
from conjureup import controllers, juju, utils, snap
from conjureup.app_config import app
from conjureup.ui.views.destroy import DestroyView
from conjureup.models.step import StepModel
from juju.model import Model


class Destroy:

    def __init__(self):
        self.view = None
        self.spells = []

    async def _query_model_config(self, controller, model):
        if not app.juju.client:
            app.juju.client = Model(app.loop)
        await app.juju.client.connect("{}:{}".format(
            controller, model))
        result = await app.juju.client.get_config()
        if 'extra-info' in result:
            try:
                return json.loads(result['extra-info'].value)
            except json.JSONDecodeError as e:
                app.log.debug("Failed to read a model config: {}".format(e))
        return None

    def finish(self, spellname):
        for spell in self.spells:
            if spellname == spell['spellname']:
                if 'controller' in spell:
                    app.provider.controller = spell['controller']
                if 'model' in spell:
                    app.provider.model = spell['model']

        utils.set_chosen_spell(spellname,
                               os.path.join(app.conjurefile['cache-dir'],
                                            spellname))
        utils.set_spell_metadata()
        StepModel.load_spell_steps()
        controllers.setup_metadata_controller()
        return controllers.use('destroyconfirm').render()

    async def query_deployments(self):
        """ Get a list of deployed spells
        """
        existing_controllers = juju.get_controllers()['controllers']
        for cname in existing_controllers.keys():
            for model in juju.get_models(cname)['models']:
                model_config = await self._query_model_config(
                    cname,
                    model['short-name'])
                self.spells.append(
                    {'spellname': model_config['config']['spell'],
                     'controller': cname,
                     'model': model})
        if snap.is_installed('microk8s'):
            self.spells.append({'spellname': 'microk8s'})

        self.view = DestroyView(app,
                                spells=self.spells,
                                cb=self.finish)
        self.view.show()

    def render(self):
        app.loop.create_task(self.query_deployments())


_controller_class = Destroy
