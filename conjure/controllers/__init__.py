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
from conjure import controllers

controllers.use('clouds').render()
or

# Render TUI version of clouds controller
from conjure.app_config import app
app.headless = True
c = controllers.use('clouds')
c.finish()
"""

from importlib import import_module
from conjure.app_config import app


def use(controller):
    """ Loads view Controller

    All controllers contain the following structure
    conjure/controllers/<controller name>/{gui,tui}.py

    Arguments:
    controller: name of view controller to Load
    """
    try:
        if app.headless:
            pkg = ("conjure.controllers.{}.tui".format(controller))
        else:
            pkg = ("conjure.controllers.{}.gui".format(controller))
        return import_module(pkg)
    except Exception as e:
        raise e
