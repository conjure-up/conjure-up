from abc import ABC, abstractmethod

""" Creating controllers based on renderer

There are 2 types of rendering, stdout and urwid. This is triggered
by passed a '-y' on the cli to trigger a headless (stdout) vs non-headless
(urwid).

Each controller will contain 3 classes, TUI (stdout), GUI (urwid), Controller.

Both TUI() and GUI() should inherit from below ControllerPolicy to make sure
we conform to providing the proper rendering and callback mechanisms.

The controller itself will define a Python class __new__ method to load
the correct rendering class based on the cli arg.

See any of the controllers for examples.
"""

class ControllerPolicy(ABC):
    @abstractmethod
    def finish(self):
        """ Callback handler after view has been rendered or submitted
        """
        pass

    @abstractmethod
    def render(self):
        """ Render a View, can be console or urwid
        """
        pass
