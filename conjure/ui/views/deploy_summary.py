""" Deployment summary view


List out the updated bundle in a cleaner view showing what
charms and their relations will be done.
"""

from urwid import WidgetWrap, Text, Pile, Columns, Filler
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.text import Instruction, ColumnHeader
from ubuntui.widgets.hr import HR
from ubuntui.utils import Color, Padding
from ubuntui.ev import EventLoop
import yaml
import q


class DeploySummaryView(WidgetWrap):
    def __init__(self, common, bundle, cb):
        """ Init

        Arguments:
        common: common config
        bundle: dictionary of bundle
        cb: callback
        """
        self.common = common
        with open(bundle) as b:
            self.bundle = yaml.load(b)
        self.cb = cb
        _pile = [
            Padding.center_90(
                Instruction(
                    "Services and Relations to be deployed and set.")),
            Padding.center_90(HR()),
            Padding.center_90(self.build_summary()),
            Padding.line_break(""),
            Padding.center_20(self._build_buttons())
        ]
        super().__init__(Filler(Pile(_pile), valign="top"))

    def _build_buttons(self):
        reset = PlainButton(label="Start Over", on_press=self.reset)
        deploy = PlainButton(label="Deploy", on_press=self.done)
        cancel = PlainButton(label="Quit", on_press=self.cancel)
        buttons = [
            Color.button_primary(deploy,
                                 focus_map='button_primary focus'),
            Color.button_secondary(reset,
                                   focus_map='button_secondary focus'),
            Color.button_secondary(cancel,
                                   focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def build_summary(self):
        """ Builds out the summary of the bundle
        """
        rows = []
        rows.append(
            Columns([
                ColumnHeader("Services"),
                ColumnHeader("Relations"),
                ColumnHeader("Machines")
            ], dividechars=1)
        )

        machines = None
        if not self.bundle['machines']:
            machines = "Machines will be autoplaced."
        else:
            machines = yaml.dump(self.bundle['machines'])

        rows.append(
            Columns(
                    [
                        Text(", ".join(self.bundle['services'].keys())),
                        Text(yaml.dump(self.bundle['relations'])),
                        Text(machines)
                    ],
                    dividechars=1
                )
            )
        return Pile(rows)

    def reset(self, button):
        self.cb(reset=True)

    def done(self, button):
        self.cb()

    def cancel(self, button):
        EventLoop.exit(0)
