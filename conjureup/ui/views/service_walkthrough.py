""" Service Walkthrough view

List out the updated bundle in a cleaner view showing what
charms and their relations will be done.
"""

from urwid import (connect_signal, Filler, WidgetWrap, Pile,
                   Text, Columns)

from conjureup.app_config import app
from conjureup.ui.widgets.option_widget import OptionWidget
from ubuntui.ev import EventLoop
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.input import IntegerEditor
from ubuntui.widgets.hr import HR
from ubuntui.utils import Color, Padding

import logging

log = logging.getLogger('conjure')


class ServiceWalkthroughView(WidgetWrap):
    def __init__(self, service, idx, n_total, metadata_controller, callback):
        self.callback = callback
        self.service = service
        self.idx = idx
        self.n_total = n_total
        self.n_remaining = n_total - idx - 1
        self.metadata_controller = metadata_controller
        self.info_handled = False
        w = self.build_widgets()
        super().__init__(w)
        self.get_async_info()
        if self.n_remaining == 0:
            self.pile.focus_position = len(self.pile.contents) - 1
        else:
            self.pile.focus_position = len(self.pile.contents) - 2

    def selectable(self):
        return True

    def build_widgets(self):
        self.description_w = Text("Description Loading…")
        self.readme_w = Text("README Loading…")
        self.scale_edit = IntegerEditor(default=self.service.num_units)
        connect_signal(self.scale_edit._edit, 'change',
                       self.handle_scale_changed)
        self.skip_rest_button = PlainButton(
            "Deploy all {} Remaining Applications with Bundle Defaults".format(
                self.n_remaining),
            self.do_skip_rest
        )
        col = Columns(
            [
                (6, Text('Units:', align='right')),
                (15,
                 Color.string_input(self.scale_edit,
                                    focus_map='string_input focus'))
            ], dividechars=1
        )

        if self.n_remaining == 0:
            buttons = [Padding.right_50(Color.button_primary(
                PlainButton("Deploy and Continue",
                            self.do_deploy),
                focus_map='button_primary focus'))]
        else:
            buttons = [
                Padding.right_50(Color.button_primary(
                    PlainButton(
                        "Deploy and Configure Next Application",
                        self.do_deploy),
                    focus_map='button_primary focus')),
                Padding.right_50(
                    Color.button_secondary(
                        self.skip_rest_button,
                        focus_map='button_secondary focus'))]

        ws = [Text("{} of {}: {}".format(self.idx+1, self.n_total,
                                         self.service.service_name.upper())),
              Padding.center(HR()),
              Padding.center(self.description_w, left=2),
              Padding.line_break(""),
              Padding.center(self.readme_w, left=2),
              Padding.center(HR())]

        if not self.service.subordinate:
            ws.append(Padding.left(col, left=1))

        ws.append(Padding.line_break(""))
        ws += buttons

        self.pile = Pile(ws)
        return Padding.center_90(Filler(self.pile, valign="top"))

    def get_async_info(self):
        info = self.metadata_controller.get_charm_info(
            self.service.csid.as_str_without_rev(),
            self.handle_info_updated)
        if info:
            self.handle_info_updated(info)

        self.metadata_controller.get_readme(
            self.service.csid.as_seriesname(),
            self.handle_readme_updated)

    def handle_info_updated(self, new_info):
        if self.info_handled:
            return
        self.info_handled = True
        EventLoop.loop.event_loop._loop.call_soon_threadsafe(
            self._update_info_on_main_thread,
            new_info)

    def _update_info_on_main_thread(self, new_info):
        self.description_w.set_text(
            new_info["Meta"]["charm-metadata"]["Summary"])
        self._invalidate()
        self.add_options()

    def add_options(self):
        service_id = self.service.csid.as_str_without_rev()
        options = self.metadata_controller.get_options(service_id)
        metadata = app.config.get('metadata', None)
        if metadata is None:
            return

        options_whitelist = metadata.get('options-whitelist', None)
        if options_whitelist is None:
            return

        svc_opts_whitelist = options_whitelist.get(self.service.service_name,
                                                   [])
        hidden = [n for n in options.keys() if n not in svc_opts_whitelist]
        log.info("Hiding options not in the whitelist: {}".format(hidden))
        for opname in svc_opts_whitelist:
            opdict = options[opname]
            self.add_option_widget(opname, opdict)

    def add_option_widget(self, opname, opdict):
        cv = self.service.options.get(opname, None)
        ow = OptionWidget(opname,
                          opdict['Type'],
                          opdict['Description'],
                          opdict['Default'],
                          current_value=cv,
                          value_changed_callback=self.handle_edit)

        self.pile.contents.insert(7, (ow, self.pile.options()))
        self._invalidate()
        return ow

    def handle_edit(self, opname, value):
        self.service.options[opname] = value

    def handle_readme_updated(self, readme_text_f):
        EventLoop.loop.event_loop._loop.call_soon_threadsafe(
            self._update_readme_on_main_thread,
            readme_text_f)

    def _update_readme_on_main_thread(self, readme_text_f):
        rls = readme_text_f.result().splitlines()
        rls = [l for l in rls if not l.startswith("#")]
        nrls = []
        for i in range(len(rls)):
            if i+1 == len(rls):
                break
            if len(rls[i]) > 0:
                if rls[i][0] in ['-', '#', '=']:
                    continue
            if len(rls[i+1]) > 0:
                if rls[i+1][0] in ['-', '=']:
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
        self.readme_w.set_text("\n".join(nrls))
        self._invalidate()

    def handle_scale_changed(self, widget, newvalstr):
        if newvalstr == '':
            return
        self.service.num_units = int(newvalstr)

    def do_deploy(self, arg):
        self.callback(single_service=self.service)

    def do_skip_rest(self, arg):
        self.callback(single_service=None)
