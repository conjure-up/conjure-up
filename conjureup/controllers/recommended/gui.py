import os

from conjureup.download import download_local, get_remote_url
from conjureup.ui.views.recommended import RecommendedSpellView
from conjureup import utils
from conjureup import controllers
from conjureup.app_config import app


class RecommendedSpellsController:
    def __init__(self):
        self.view = None

    def __handle_exception(self, exc):
        utils.pollinate(app.session_id, "TODO")
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
        return controllers.use('clouds').render()

    def render(self):
        recs = []

        for _, kd in app.spells_index.items():

            recs += kd['spells']

        view = RecommendedSpellView(app,
                                    recs,
                                    self.finish)

        app.ui.set_header(
            title="Choose a Spell",
            excerpt="Choose from this list of recommended spells"
        )
        app.ui.set_body(view)


_controller_class = RecommendedSpellsController
