""" Creating controllers based on renderer

There are 2 types of rendering, stdout and urwid. This is triggered
by passed a '-y' on the cli to trigger a headless (stdout) vs non-headless
(urwid).

Each controller will contain 3 classes, TUI (stdout), GUI (urwid), Controller.

Both TUI() and GUI() should provide at least an entry method (render) and an
exit method (finish). This is not a hard rule but it is documented here so that
the controllers can stay consistent in their execution.

The controller itself will define a module level function to load
the correct rendering class based on the cli arg.

See any of the controllers for examples.
"""
