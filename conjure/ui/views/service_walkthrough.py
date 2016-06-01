""" Service Walkthrough view

List out the updated bundle in a cleaner view showing what
charms and their relations will be done.
"""

from urwid import (connect_signal, Filler, WidgetWrap, Pile,
                   Text, Columns)
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.input import IntegerEditor
from ubuntui.widgets.hr import HR
from ubuntui.utils import Color, Padding


class ServiceWalkthroughView(WidgetWrap):
    def __init__(self, service, idx, n_total, metadata_controller, callback):
        self.callback = callback
        self.service = service
        self.idx = idx
        self.n_total = n_total
        self.n_remaining = n_total - idx - 1
        self.metadata_controller = metadata_controller
        w = self.build_widgets()
        super().__init__(w)
        self.pile.focus_position = 8

    def selectable(self):
        return True

    def build_widgets(self):
        self.description_w = Text("Description Loading…")
        info = self.metadata_controller.get_charm_info(
            self.service.csid.as_str_without_rev(),
            self.handle_info_updated)
        if info:
            self.handle_info_updated(info)
        self.readme_w = Text("README Loading…")

        self.metadata_controller.get_readme(
            self.service.csid.as_seriesname(),
            self.handle_readme_updated)
        self.scale_edit = IntegerEditor(default=1)
        connect_signal(self.scale_edit._edit, 'change',
                       self.handle_scale_changed)
        self.continue_button = PlainButton(
            "Deploy and Configure Next Application",
            self.do_deploy)
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
        ws = [Text("{} of {}: {}".format(self.idx+1, self.n_total,
                                         self.service.service_name.upper())),
              Padding.center(HR()),
              Padding.center(self.description_w, left=2),
              Padding.line_break(""),
              Padding.center(self.readme_w, left=2),
              Padding.center(HR()),
              Padding.left(col, left=1),
              Padding.line_break(""),
              Padding.right_50(
                  Color.button_primary(self.continue_button,
                                       focus_map='button_primary focus')),
              Padding.right_50(
                  Color.button_secondary(self.skip_rest_button,
                                         focus_map='button_secondary focus'))]

        self.pile = Pile(ws)
        return Padding.center_90(Filler(self.pile, valign="top"))

    def handle_info_updated(self, new_info):
        self.description_w.set_text(
            new_info["Meta"]["charm-metadata"]["Summary"])
        # TODO MMCC save metadata and use options here

    def handle_readme_updated(self, readme_text_f):
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
        if nrls[0] == '':
            nrls = nrls[1:]
        # split after two paragraphs:
        firstparidx = nrls.index('')
        try:
            splitidx = nrls.index('', firstparidx + 1)
        except:
            splitidx = firstparidx
        nrls = nrls[:splitidx]
        self.readme_w.set_text("\n".join(nrls))

    def handle_scale_changed(self, widget, newvalstr):
        if newvalstr == '':
            return
        self.service.num_units = int(newvalstr)

    def do_deploy(self, arg):
        self.callback(service=self.service)

    def do_skip_rest(self, arg):
        self.callback(service=None)
