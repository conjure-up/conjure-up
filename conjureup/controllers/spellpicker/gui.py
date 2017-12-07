import os

from conjureup import controllers, utils
from conjureup.app_config import app
from conjureup.download import EndpointType, download_local
from conjureup.models.addon import AddonModel
from conjureup.models.step import StepModel
from conjureup.ui.views.spellpicker import SpellPickerView


class SpellPickerController:
    def finish(self, spellname):
        utils.set_terminal_title("conjure-up {}".format(spellname))
        utils.set_chosen_spell(spellname,
                               os.path.join(app.argv.cache_dir,
                                            spellname))
        download_local(os.path.join(app.config['spells-dir'],
                                    spellname),
                       app.config['spell-dir'])
        utils.set_spell_metadata()
        StepModel.load_spell_steps()
        AddonModel.load_spell_addons()
        utils.setup_metadata_controller()
        return controllers.use('addons').render()

    def render(self):
        spells = []
        if app.endpoint_type is None:
            spells += utils.find_spells()
        elif app.endpoint_type == EndpointType.LOCAL_SEARCH:
            spells = utils.find_spells_matching(app.argv.spell)
        else:
            raise Exception("Unexpected endpoint type {}".format(
                app.endpoint_type))

        # add subdir of spells-dir to spell dict for bundle readme view:
        for category, spell in spells:
            spell['spell-dir'] = os.path.join(app.config['spells-dir'],
                                              spell['key'])

        def spellcatsorter(t):
            cat = t[0]
            name = t[1]['name']
            if cat == '_unassigned_spells':
                return ('z', name)
            return (cat, name)

        view = SpellPickerView(app,
                               sorted(spells,
                                      key=spellcatsorter),
                               self.finish)
        view.show()


_controller_class = SpellPickerController
