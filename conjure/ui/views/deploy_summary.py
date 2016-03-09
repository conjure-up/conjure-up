""" Deployment summary view


List out the updated bundle in a cleaner view showing what
charms and their relations will be done.
"""

from urwid import WidgetWrap, Text, Pile, Columns, Filler
from ubuntui.widgets.buttons import (cancel_btn, confirm_btn)
from ubuntui.widgets.text import Instruction, ColumnHeader
from ubuntui.widgets.hr import HR
from ubuntui.utils import Color, Padding
from ubuntui.ev import EventLoop
import yaml


class DeploySummaryView(WidgetWrap):
    def __init__(self, common, bundle, cb):
        """ Init

        Arguments:
        common: common config
        bundle: dictionary of bundle
        cb: callback
        """
        self.common = common
        self.bundle = bundle
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
        cancel = cancel_btn(on_press=self.cancel)
        deploy = confirm_btn(label="Deploy", on_press=self.done)
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
            Columns([
                ColumnHeader("Services"),
                ColumnHeader("Relations")
            ], dividechars=1)
        )
        services = ", ".join(self.bundle['services'].keys())
        rows.append(
            Columns(
                    [
                        Text(services),
                        Text(yaml.dump(self.bundle['relations']))
                    ],
                    dividechars=1
                )
            )
        return Pile(rows)

    def cancel(self, button):
        EventLoop.exit(0)

    def done(self, result):
        self.cb()
