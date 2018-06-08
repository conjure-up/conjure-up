""" Creating controllers based on renderer

There are 2 types of rendering, stdout and urwid. This is triggered
by passed a '-y' on the cli to trigger a headless (stdout) vs non-headless
(urwid).

Each controller will contain 2 modules, TUI (stdout) and GUI (urwid).

Both TUI() and GUI() should provide at least an entry method (render) and an
exit method (finish). This is a hard rule and is documented here so that
the controllers can stay consistent in their execution. All other functions
in their respective module should be prepended with double underscore '__'
as they should only be relevant to that module.

If both renderers share code place those functions inside a `common.py` module
and import relative to the render module, for example (from newcloud
controller),

from .common import check_bridge_exists

See any of the controllers for examples.

Usage:

# Render GUI version of clouds controller
from conjureup import controllers

controllers.use('clouds').render()
or

# Render TUI version of clouds controller
from conjureup.app_config import app
app.headless = True
c = controllers.use('clouds')
c.finish()
"""

from functools import lru_cache
from importlib import import_module

from conjureup import events, consts
from conjureup.app_config import app
import yaml
from conjureup import charm
from conjureup.utils import slurp
from conjureup.bundle import Bundle
from pathlib import Path
from itertools import chain


def setup_metadata_controller():
    """ Load metadata controller based on spell_type
    """
    if app.metadata.spell_type == consts.spell_types.SNAP:
        return _setup_snap_metadata_controller()

    # This is the typical default for now
    return _setup_juju_metadata_controller()


def _setup_snap_metadata_controller():
    """ Sets metadata for a snap spell
    """
    return


def _setup_juju_metadata_controller():
    """ Pulls in a local bundle or via charmstore api and sets up our
    controller. You can also further customize the bundle by providing a local
    bundle-custom.yaml that will be deep merged over whatever bundle is
    referenced. """
    spell_dir = Path(app.config['spell-dir'])
    bundle_filename = spell_dir / 'bundle.yaml'
    bundle_custom_filename = spell_dir / 'bundle-custom.yaml'
    if bundle_filename.exists():
        # Load bundle data early so we can merge any additional charm options
        bundle_data = Bundle(yaml.load(bundle_filename.read_text()))
    else:
        bundle_name = app.metadata.bundle_name
        if bundle_name is None:
            raise Exception(
                "Could not determine a bundle to download, please make sure "
                "the spell contains a 'bundle-name' field."
            )
        bundle_channel = app.conjurefile['channel']

        app.log.debug("Pulling bundle for {} from channel: {}".format(
            bundle_name, bundle_channel))
        bundle_data = Bundle(charm.get_bundle(bundle_name, bundle_channel))

    if bundle_custom_filename.exists():
        bundle_custom = yaml.load(slurp(bundle_custom_filename))
        bundle_data.apply(bundle_custom)

    for name in app.selected_addons:
        addon = app.addons[name]
        bundle_data.apply(addon.bundle)

    steps = list(chain(app.steps,
                       chain.from_iterable(app.addons[addon].steps
                                           for addon in app.selected_addons)))
    for step in steps:
        if not (step.bundle_add or step.bundle_remove):
            continue
        if step.bundle_remove:
            fragment = yaml.safe_load(step.bundle_remove.read_text())
            bundle_data.subtract(fragment)
        if step.bundle_add:
            fragment = yaml.safe_load(step.bundle_add.read_text())
            bundle_data.apply(fragment)

    if app.conjurefile['bundle-remove']:
        fragment = yaml.safe_load(app.conjurefile['bundle-remove'].read_text())
        bundle_data.subtract(fragment)
    if app.conjurefile['bundle-add']:
        fragment = yaml.safe_load(app.conjurefile['bundle-add'].read_text())
        bundle_data.apply(fragment)

    app.current_bundle = bundle_data


@lru_cache(maxsize=None)
def use(controller):
    """ Loads view Controller

    All controllers contain the following structure
    conjure/controllers/<controller name>/{gui,tui}.py

    Arguments:
    controller: name of view controller to Load
    """
    if events.Error.is_set() or events.Shutdown.is_set():
        # once an error has been encountered or a shutdown issued
        # we don't want to allow any new controllers to be rendered
        return NoopController()

    if app.headless:
        pkg = ("conjureup.controllers.{}.{}.tui".format(
            app.metadata.spell_type,
            controller))
    else:
        pkg = ("conjureup.controllers.{}.{}.gui".format(
            app.metadata.spell_type, controller))
    module = import_module(pkg)
    if '_controller_class' in dir(module):
        return module._controller_class()
    else:
        return module


class NoopController:
    def render(self, *args, **kwargs):
        pass
