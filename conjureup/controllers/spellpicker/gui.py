import os

from conjureup import controllers, utils
from conjureup.app_config import app
from conjureup.download import EndpointType, download_local
from conjureup.ui.views.spellpicker import SpellPickerView


class SpellPickerController:

    def __init__(self):
        self.view = None

    def __handle_exception(self, exc):
        utils.pollinate(app.session_id, "E005")
        app.ui.show_exception_message(exc)

    def finish(self, spellname):

        utils.pollinate(app.session_id, 'CS')

        utils.set_chosen_spell(spellname,
                               os.path.join(app.argv.cache_dir,
                                            spellname))
        download_local(os.path.join(app.config['spells-dir'],
                                    spellname),
                       app.config['spell-dir'])
        utils.set_spell_metadata()
        utils.setup_metadata_controller()
        return controllers.use('controllerpicker').render()

    def render(self):
        spells = []

        if app.endpoint_type is None:
            for _, kd in app.spells_index.items():
                spells += kd['spells']
        elif app.endpoint_type == EndpointType.LOCAL_SEARCH:
            spells = utils.find_spells_matching(app.argv.spell)
        else:
            e = Exception("Unexpected endpoint type {}".format(
                app.endpoint_type))
            app.ui.show_exception_message(e)

        # add subdir of spells-dir to spell dict for bundle readme view:
        for spell in spells:
            spell['spell-dir'] = os.path.join(app.config['spells-dir'],
                                              spell['key'])
        view = SpellPickerView(app,
                               sorted(spells, key=lambda kv: kv['name']),
                               self.finish)

        app.ui.set_header(
            title="Spell Selection",
            excerpt="Choose from this list of recommended spells"
        )
        app.ui.set_body(view)


_controller_class = SpellPickerController
