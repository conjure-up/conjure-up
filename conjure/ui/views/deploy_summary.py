""" Deployment summary view


List out the updated bundle in a cleaner view showing what
charms and their relations will be done.
"""

from urwid import WidgetWrap, Text, Pile, Columns, Filler
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.text import Instruction, ColumnHeader
from ubuntui.widgets.hr import HR
from ubuntui.utils import Color, Padding
import yaml


class DeploySummaryView(WidgetWrap):
    def __init__(self, app, bundle, cb):
        """ Init

        Arguments:
        app: app config
        bundle: dictionary of bundle
        cb: callback
        """
        self.app = app
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
        deploy = PlainButton(label="Deploy", on_press=self.done)
        cancel = PlainButton(label="Cancel", on_press=self.cancel)
        buttons = [
            Color.button_primary(deploy,
                                 focus_map='button_primary focus'),
            Color.button_secondary(cancel,
                                   focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def build_summary(self):
        """ Builds out the summary of the bundle
        """
        rows = []
        rows.append(
            Text("You will be deploying these services: {}.  ".format(
                ", ".join(self.bundle['services'].keys())
            )))

        machines = None
        if not self.bundle['machines']:
            machines = ("They will be autoplaced across multiple containers.")
        else:
            machines = ("They will be placed across the {} machine(s) "
                        "selected in the previous view.".format(
                            len(self.bundle['machines'].keys())
                        ))
        rows.append(Padding.line_break(""))
        rows.append(Text(machines))
        rows.append(Padding.line_break(""))

        return Pile(rows)

    def done(self, button):
        self.cb()

    def cancel(self, button):
        self.cb(back=True)
