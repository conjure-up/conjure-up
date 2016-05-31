""" Service Walkthrough view

List out the updated bundle in a cleaner view showing what
charms and their relations will be done.
"""

from urwid import (connect_signal, Divider, Filler, WidgetWrap, Pile,
                   Text, Padding)
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.input import IntegerEditor


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

    def selectable(self):
        return True

    def build_widgets(self):
        self.description_w = Text("Description Loading…")
        self.metadata_controller.get_charm_info(
            self.service.csid.as_str_without_rev(),
            self.handle_info_updated)
        self.readme_w = Text("README Loading…")

        self.metadata_controller.get_readme(
            self.service.csid.as_seriesname(),
            self.handle_readme_updated)
        self.scale_edit = IntegerEditor(caption="Units: ", default=1)
        connect_signal(self.scale_edit._edit, 'change',
                       self.handle_scale_changed)
        self.continue_button = PlainButton("Deploy and Configure Next Service",
                                           self.do_deploy)
        self.skip_rest_button = PlainButton(
            "Deploy all {} Remaining Services with Bundle Defaults".format(
                self.n_remaining),
            self.do_skip_rest
        )
        ws = [Text("{}/{}: {}".format(self.idx+1, self.n_total,
                                      self.service.service_name)),
              Padding(self.description_w, left=2),
              Divider(),
              Padding(self.readme_w, left=2),
              Divider(),
              Padding(self.scale_edit, align='right'),
              Padding(self.continue_button,
                      align='right', width=70),
              Padding(self.skip_rest_button,
                      align='right', width=70)]

        self.pile = Pile(ws)
        return Padding(Filler(self.pile, valign="middle"),
                       align="center", width=('relative', 60))

    def handle_info_updated(self, new_info):
        self.description_w.set_text(
            new_info["Meta"]["charm-metadata"]["Summary"])
        # TODO MMCC save metadata and use options here

    def handle_readme_updated(self, readme_text_f):
        rls = readme_text_f.result().splitlines()
        rls = [l for l in rls if not l.startswith("#")]
        nrls = []
        for i in range(len(rls)):
            if len(nrls) == 20:
                break
            if i+1 == len(rls):
                break
            if rls[i].startswith("+") or rls[i+1].startswith("="):
                continue
            nrls.append(rls[i])
        self.readme_w.set_text("\n".join(nrls))

    def handle_scale_changed(self, widget, newvalstr):
        if newvalstr == '':
            return
        self.service.num_units = int(newvalstr)

    def do_deploy(self, arg):
        self.callback(service=self.service)

    def do_skip_rest(self, arg):
        self.callback(service=None)
