# Getting a development environment started

0. clone the repo
1. `make sysdeps`
2. `make dev`
3. `source conjure-dev/bin/activate`
4. `make test`

# Check tests before submitting a PR

While the unit test suite coverage is low enough that most changes
won't affect the test results (yes this is bad), the Travis test suite
checks lint, so it's a good idea to run the tests anyway before submitting:

```
% make test
```

If you see isort or pep8 errors, e.g. due to imports being out of
order, fix it automatically with this:

```
% make auto-format
```

# Release procedures
TODO - need more details on version updates, etc.

## Building the snap

```
% make release-snap
```

# Architecture notes
## General flow
The UI is structured as a sequence of screens, represented by controllers in `conjureup/controllers/`.
Each controller has a `render()` function and a `finish()` function. `render()` creates the urwid widgets for the UI for that screen, and for dynamic views, starts their update timers. `finish()` is called by the UI when it's time to commit changes on that screen and move to the next controller.

If run in 'headless' mode, the controllers used will be the ones in `conjureup/controllers/$controllername/tui.py`. If used in default GUI mode, the corresponding `gui.py` code will execute. In some cases the code in `tui.py` does very little.

## Understanding controller flow

There's a script that outputs diagrams showing the flow through the various controllers at `tools/graph-controllers.py`. Run it with no arguments and you get two files in ASCII box art, one for each of the GUI and TUI modes.

Here's the output against master as of this commit. The graph starts at the START box, and each other box is the name of the controller. Each edge is annotated with the function name and line number in the file where the transition is made.
```
                                            +---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
                                              |                                                                                                                                                                                             |
                                              |                                                                                                                                                                                             |
                                              |                                                                                                                                                                                             |    +------------------------------------+
                                              |                                                                                                                                                                                             |    |                                    |
               finish:44                      |                                                           _start:135                                                                                                                        |    |        render:176                  |
  +-------------------------------------------+----+                                            +------------------------------------------------------------------------------------------------------------------+                        |    |    +-------------------+           |
  v                                           |    |                                            |                                                                                                                  v                        |    |    |                   v           |
+------------+                                |  +----------------------------+  _start:131   +---------+  _start:113                 +----------------+  finish:24    +------------------+  finish:21           +--------+  finish:24    +-------------+  render:163   +----------+  |
|   steps    |  +-----------------------------+> |        deploystatus        | <------------ |  START  | --------------------------> |  spellpicker   | ------------> |                  | -------------------> |        | ------------> |             | ------------> |          |  |
+------------+  |                             |  +----------------------------+               +---------+                             +----------------+               |                  |                      |        |               |             |               |          |  |
  |             |                             |    ^                                            |                                                        _start:138    |                  |  render:41           |        |  finish:129   |             |  render:169   |          |  |
  | finish:74   |                             |    | finish:17                                  +--------------------------------------------------------------------> | controllerpicker | -------------------> | clouds | <------------ |  newcloud   | ------------> | lxdsetup |  |
  v             |                             |    |                                                                                                                   |                  |                      |        |               |             |               |          |  |
+------------+  |                             |  +----------------------------+                           __handle_destroy_done:31                                     |                  |  render:58           |        |               |             |               |          |  |
|  summary   |  |                             |  |       bootstrapwait        |                 +---------------------------------------+                              |                  | -------------------> |        |               |             |  +----------- |          |  |
+------------+  |                             |  +----------------------------+                 v                                       |                              +------------------+                      +--------+               +-------------+  |            +----------+  |
                |                             |    ^                                          +---------+  finish:17                  +----------------+                 |                                              ^   finish:51                 ^    |              |           |
                |                             |    | enqueue_set_relations:353                | destroy | --------------------------> | destroyconfirm |                 | finish:36                                    +-----------------------------+----+              |           |
                |                             |    |                                          +---------+                             +----------------+                 v                                                                            |                   |           |
                |                             |    |                                            ^         finish:38                     |                              +------------------+                                                           |   finish:81       |           |
                | enqueue_set_relations:355   |    |                                            +---------------------------------------+                              |                  |                                                           +-------------------+           |
                |                             |    |                                                                                                                   |                  |                                                                                           |
                |                             |    |                                                                                                                   |                  |                                                                                           |
                |                             |    +------------------------------------------------------------------------------------------------------------------ |      deploy      |                                                                                           |
                |                             |                                                                                                                        |                  |                                                                                           |
                |                             |                                                                                                          render:195    |                  |                                                                                           |
                |                             +----------------------------------------------------------------------------------------------------------------------> |                  | -----------------------+                                                                  |
                |                                                                                                                                                      +------------------+                        |                                                                  |
                |                                                                                                                                                        ^                  __do_bootstrap:73      |                                                                  |
                |                                                                                                                                                        +-----------------------------------------+------------------------------------------------------------------+
                |                                                                                                                                                                                                  |
                |                                                                                                                                                                                                  |
                +--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```

## Dynamic urwid views
The more complex screens use urwid timers to dynamically change the UI, and have significant logic in View classes (in [conjureup/ui/views/](https://github.com/conjure-up/conjure-up/blob/master/conjureup/ui/views) The most complex example is the deploy screen ([controllers/deploy/gui.py](https://github.com/conjure-up/conjure-up/blob/master/conjureup/controllers/deploy/gui.py)), which encapsulates the main application list UI in classes defined in [ui/views/applicationlist.py](https://github.com/conjure-up/conjure-up/blob/master/conjureup/ui/views/applicationlist.py), and the application architecture view is separately defined in [ui/views/app_architecture_view.py](https://github.com/conjure-up/conjure-up/blob/master/conjureup/ui/views/app_architecture_view.py). Both views are managed by the same controller, which maintains some state necessary for deployment, such as the current application<-> machine assignments, and maas-machine <-> juju_machine pins.

These view classes are usually implemented as Urwid WidgetWrap subclasses, which are just a convenience for packaging up a bunch of widgets together with some management logic. Typically they start by building their main structure with a `build_widgets()` function called once in `__init__()`, and then call `update()` to build any dynamic widgets, or update the pre-existing widgets to change their contents based on current state. `update()` usually starts a timer to call itself again periodically, but it is also sometimes called directly in callbacks, e.g. when the MAAS api returns with a list of machines, so we don't have to wait for a timer to fire to update the list.

