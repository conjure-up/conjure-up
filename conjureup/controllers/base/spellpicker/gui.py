import asyncio
import json
import os

from conjureup import controllers, utils, snap, juju
from conjureup.app_config import app
from conjureup.download import EndpointType, download_local
from conjureup.models.addon import AddonModel
from conjureup.models.step import StepModel
from conjureup.ui.views.spellpicker import SpellPickerView
from juju.errors import JujuConnectionError
from juju.model import Model


class SpellPickerController:
    def _get_deployed_spell(self, key):
        """ Shows list of deployed spells
        """
    def finish(self, spell):
        spellname = spell['key']
        if spellname != app.config.get('spell'):
            utils.set_terminal_title("conjure-up {}".format(spellname))
            utils.set_chosen_spell(spellname,
                                   os.path.join(app.conjurefile['cache-dir'],
                                                spellname))
            download_local(os.path.join(app.config['spells-dir'],
                                        spellname),
                           app.config['spell-dir'])
            utils.set_spell_metadata()
            StepModel.load_spell_steps()
            AddonModel.load_spell_addons()
            controllers.setup_metadata_controller()
        if app.conjurefile['destroy']:
            return controllers.use('showsteps').render()
        else:
            return controllers.use('addons').render()

    async def _query_model_config(self, controller, model):
        if not app.juju.client:
            app.juju.client = Model(app.loop)
        target = "{}:{}".format(controller, model)
        try:
            # TODO: this could take a while; we should show an interstitial
            await asyncio.wait_for(app.juju.client.connect(target), 30)
        except (JujuConnectionError, asyncio.TimeoutError):
            app.log.debug('Unable to connect to {}; skipping'.format(target))
            return {}
        result = await app.juju.client.get_config()
        if 'extra-info' in result:
            extra_info = result['extra-info'].value
        else:
            extra_info = None
        app.log.debug('extra-info for {}:{}: {}'.format(controller,
                                                        model,
                                                        extra_info))
        if extra_info:
            try:
                result = json.loads(result['extra-info'].value)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass
        app.log.debug("Ignoring unintelligble model config for {}:{}: "
                      "{}".format(controller, model, extra_info))
        return {}

    async def query_deployments(self, spells):
        """ Get a list of deployed spells
        """
        existing_controllers = juju.get_controllers()['controllers']
        for cname in existing_controllers.keys():
            # TODO: this could take a while; we should show an interstitial
            models = juju.get_models(cname)
            if not models:
                continue
            for model in models['models']:
                if model['short-name'] == 'controller':
                    continue
                model_config = await self._query_model_config(
                    cname,
                    model['short-name'])
                spell_name = model_config.get('config', {}).get('spell',
                                                                '(unknown)')

                for cat, _spell in spells:
                    if _spell['key'] == 'microk8s' and \
                       snap.is_installed('microk8s'):
                        _spell['deploys'] = [
                            {'controller': None, 'model': None}
                        ]

                    if _spell['key'] == spell_name:
                        if 'deploys' in _spell:
                            _spell['deploys'].append(
                                {'controller': cname,
                                 'model': model['short-name']})
                        else:
                            _spell['deploys'] = [
                                {'controller': cname,
                                 'model': model['short-name']}
                            ]

                if not any([spell_name == spell['key']
                            for _, spell in spells]):
                    spells.append(('_unassigned_spells',
                                   {'key': spell_name,
                                    'name': 'Custom spell: {}'.format(
                                        spell_name),
                                    'description': '',
                                    'deploys': [
                                        {'controller': cname,
                                         'model': model['short-name']}
                                    ]}))

        view = SpellPickerView(app,
                               sorted(spells,
                                      key=self._spellcatsorter),
                               self.finish)
        view.show()

    def _spellcatsorter(self, t):
        cat = t[0]
        name = t[1]['name']
        if cat == '_unassigned_spells':
            return ('z', name)
        return (cat, name)

    def render(self):
        spells = []
        if app.endpoint_type is None:
            spells += utils.find_spells()
        elif app.endpoint_type == EndpointType.LOCAL_SEARCH:
            spells = utils.find_spells_matching(app.conjurefile['spell'])
        else:
            raise Exception("Unexpected endpoint type {}".format(
                app.endpoint_type))

        # add subdir of spells-dir to spell dict for bundle readme view:
        for category, spell in spells:
            spell['spell-dir'] = os.path.join(app.config['spells-dir'],
                                              spell['key'])

        if app.conjurefile['destroy']:
            app.loop.create_task(self.query_deployments(spells))
        else:
            view = SpellPickerView(app,
                                   sorted(spells,
                                          key=self._spellcatsorter),
                                   self.finish)
            view.show()


_controller_class = SpellPickerController
