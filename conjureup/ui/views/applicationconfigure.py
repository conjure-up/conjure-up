""" Application Configuration View

"""

import logging
from functools import partial

from urwid import Columns, Filler, Frame, Pile, Text, WidgetWrap

from conjureup import utils
from conjureup.ui.widgets.option_widget import OptionWidget
from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from ubuntui.widgets.hr import HR

log = logging.getLogger('conjure')


class ApplicationConfigureView(WidgetWrap):

    def __init__(self, application, metadata_controller, controller):
        self.controller = controller
        self.application = application
        self.options_copy = self.application.options.copy()
        self.metadata_controller = metadata_controller
        self.widgets = self.build_widgets()
        self.description_w = Text("")
        self.buttons_selected = False
        self.frame = Frame(body=self.build_widgets(),
                           footer=self.build_footer())
        super().__init__(self.frame)

        self.metadata_controller.get_readme(
            self.application.csid.as_seriesname(),
            partial(self._handle_readme_load))

    def _handle_readme_load(self, readme_f):
        EventLoop.loop.event_loop._loop.call_soon_threadsafe(
            partial(self._update_readme_on_main_thread,
                    readme_f.result()))

    def _update_readme_on_main_thread(self, readme):
        rt = self._trim_readme(readme)
        self.description_w.set_text(rt)

    def _trim_readme(self, readme):
        rls = readme.splitlines()
        rls = [l for l in rls if not l.startswith("#")]
        nrls = []
        for i in range(len(rls)):
            if i + 1 == len(rls):
                break
            if len(rls[i]) > 0:
                if rls[i][0] in ['-', '#', '=']:
                    continue
            if len(rls[i + 1]) > 0:
                if rls[i + 1][0] in ['-', '=']:
                    continue
            nrls.append(rls[i])

        if len(nrls) == 0:
            return

        if nrls[0] == '':
            nrls = nrls[1:]
        # split after two paragraphs:
        if '' in nrls:
            firstparidx = nrls.index('')
        else:
            firstparidx = 1
        try:
            splitidx = nrls.index('', firstparidx + 1)
        except:
            splitidx = firstparidx
        nrls = nrls[:splitidx]
        return "\n".join(nrls)

    def selectable(self):
        return True

    def keypress(self, size, key):
        # handle keypress first, then get new focus widget
        rv = super().keypress(size, key)
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return rv

    def _swap_focus(self):
        if not self.buttons_selected:
            self.buttons_selected = True
            self.frame.focus_position = 'footer'
            self.buttons.focus_position = 3
        else:
            self.buttons_selected = False
            self.frame.focus_position = 'body'

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
        self.pile = Pile(ws)
        return Padding.center_90(Filler(self.pile, valign="top"))

    def build_footer(self):
        cancel = menu_btn(on_press=self.do_cancel,
                          label="\n  BACK\n")
        confirm = menu_btn(on_press=self.do_commit,
                           label="\n APPLY CHANGES\n")
        self.buttons = Columns([
            ('fixed', 2, Text("")),
            ('fixed', 13, Color.menu_button(
                cancel,
                focus_map='button_primary focus')),
            Text(""),
            ('fixed', 20, Color.menu_button(
                confirm,
                focus_map='button_primary focus')),
            ('fixed', 2, Text(""))
        ])

        footer = Pile([
            HR(top=0),
            Padding.center_90(self.description_w),
            Padding.line_break(""),
            Color.frame_footer(Pile([
                Padding.line_break(""),
                self.buttons]))
        ])

        return footer

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
