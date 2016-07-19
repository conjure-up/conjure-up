from conjure.ui.views.variant import VariantView
from conjure import utils
from conjure import controllers
from conjure.app_config import app
from conjure.download import download, get_remote_url
import sys
import json
import os.path as path


class VariantsController:
    def __init__(self):
        self.view = None

    def finish(self, spell):
        """ Finalizes and downloads chosen variant

        Arguments:
        spell: dictionary of charm/bundle to use
        """
        app.current_bundle = spell['Meta']['bundle-metadata']

        spell_name = spell['Meta']['id']['Name']

        # Check cache dir for spells
        spell_dir = path.join(app.config['spell-dir'],
                              spell_name)

        app.log.debug("Chosen spell: {}".format(spell_name))
        utils.pollinate(app.session_id, 'B001')

        metadata_path = path.join(spell_dir,
                                  'conjure/metadata.json')

        remote = get_remote_url(spell['Id'])
        purge_top_level = True
        if remote is not None:
            if app.fetcher == "charmstore-search" or \
               app.fetcher == "charmstore-direct":
                purge_top_level = False
            download(remote, spell_dir, purge_top_level)
        else:
            utils.warning("Could not find spell: {}".format(spell))
            sys.exit(1)

        with open(metadata_path) as fp:
            metadata = json.load(fp)

        app.config = {'metadata': metadata,
                      'spell-dir': spell_dir,
                      'spell': spell_name}

        return controllers.use('bundlereadme').render()

    def render(self):
        self.view = VariantView(self.finish)
        app.log.debug("Rendering GUI controller for Variant")
        utils.pollinate(app.session_id, 'W001')
        app.ui.set_header(
            title='Please choose a spell to conjure'
        )
        app.ui.set_body(self.view)


_controller_class = VariantsController
