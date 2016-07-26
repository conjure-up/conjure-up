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

from conjureup.app_config import app


@lru_cache(maxsize=None)
def use(controller):
    """ Loads view Controller

    All controllers contain the following structure
    conjure/controllers/<controller name>/{gui,tui}.py

    Arguments:
    controller: name of view controller to Load
    """
    try:
        if app.headless:
            pkg = ("conjureup.controllers.{}.tui".format(controller))
        else:
            pkg = ("conjureup.controllers.{}.gui".format(controller))
        module = import_module(pkg)
        if '_controller_class' in dir(module):
            return module._controller_class()
        else:
            return module
    except Exception as e:
        raise e
