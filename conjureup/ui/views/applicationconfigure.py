""" Application Configuration View

"""

import logging

from urwid import Filler, Pile, Text, WidgetWrap

from conjureup import utils
from conjureup.ui.widgets.option_widget import OptionWidget
from ubuntui.utils import Padding
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.hr import HR

log = logging.getLogger('conjure')


class ApplicationConfigureView(WidgetWrap):

    def __init__(self, application, metadata_controller, controller):
        self.controller = controller
        self.application = application
        self.options_copy = self.application.options.copy()
        self.metadata_controller = metadata_controller
        self.widgets = self.build_widgets()
        super().__init__(self.widgets)
        self.pile.focus_position = 1

    def selectable(self):
        return True

    def build_widgets(self):
        ws = [Text("Configure {}".format(
            self.application.service_name))]
        num_unit_ow = OptionWidget("Units", "int",
                                   "How many units to deploy.",
                                   self.application.orig_num_units,
                                   current_value=self.application.num_units,
                                   value_changed_callback=self.handle_scale)
        ws.append(num_unit_ow)
        ws += self.get_option_widgets()
        ws += [HR(), PlainButton("Cancel", self.do_cancel),
               PlainButton("Accept Changes", self.do_commit)]
        self.pile = Pile(ws)
        return Padding.center_90(Filler(self.pile, valign="top"))

    def get_option_widgets(self):
        ws = []
        service_id = self.application.csid.as_str_without_rev()
        options = self.metadata_controller.get_options(service_id)

        svc_opts_whitelist = utils.get_options_whitelist(
            self.application.service_name)
        hidden = [n for n in options.keys() if n not in svc_opts_whitelist]
        log.info("Hiding options not in the whitelist: {}".format(hidden))
        for opname in svc_opts_whitelist:
            opdict = options[opname]
            cv = self.application.options.get(opname, None)
            ow = OptionWidget(opname,
                              opdict['Type'],
                              opdict['Description'],
                              opdict['Default'],
                              current_value=cv,
                              value_changed_callback=self.handle_edit)
            ws.append(ow)
        return ws

    def handle_edit(self, opname, value):
        self.options_copy[opname] = value

    def handle_scale(self, opname, scale):
        self.application.num_units = scale

    def do_cancel(self, sender):
        self.controller.handle_configure_done()

    def do_commit(self, sender):
        self.application.options = self.options_copy
        self.controller.handle_configure_done()
