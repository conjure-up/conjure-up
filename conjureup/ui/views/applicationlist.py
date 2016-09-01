""" Application List view

"""
import logging
from functools import partial

from urwid import Columns, Filler, Pile, Text, WidgetWrap

from conjureup.app_config import app
from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.hr import HR

log = logging.getLogger('conjure')


class ApplicationWidget(WidgetWrap):

    def __init__(self, application, maxlen, controller, deploy_cb):
        self.application = application
        self.controller = controller
        self.deploy_cb = deploy_cb
        self._selectable = True
        super().__init__(self.build_widgets(maxlen))
        self.columns.focus_position = len(self.columns.contents) - 1

    def __repr__(self):
        return "<ApplicationWidget for {}>".format(
            self.application.service_name)

    def selectable(self):
        return self._selectable

    def build_widgets(self, maxlen):
        num_str = "{}".format(self.application.num_units)
        col_pad = 6

        cws = [
            (maxlen + col_pad,
             Text(self.application.service_name)),
            (7 + len(num_str), Text('Units: {}'.format(num_str),
                                    align='right')),
            # placeholder for instance type
            ('weight', 1, Text(" ")),
            (20, Color.button_secondary(
                PlainButton("Configure",
                            partial(self.controller.do_configure,
                                    self.application)),
                focus_map='button_secondary focus')),
            (20, Color.button_primary(
                PlainButton("Deploy",
                            partial(self.deploy_cb,
                                    self.application)),
                focus_map='button_primary focus'))
        ]
        self.columns = Columns(cws, dividechars=1)
        return self.columns

    def remove_buttons(self):
        self._selectable = False
        self.columns.contents = self.columns.contents[:-2]
        self.columns.contents.append((Text(""),
                                      self.columns.options()))

    def set_progress(self, progress_str):
        self.columns.contents[-1] = (Text(progress_str, align='right'),
                                     self.columns.options())


class ApplicationListView(WidgetWrap):

    def __init__(self, applications, metadata_controller, controller):
        self.controller = controller
        self.applications = applications
        assert(len(applications) > 0)
        self.metadata_controller = metadata_controller
        self.n_remaining = len(self.applications)
        self.widgets = self.build_widgets()
        super().__init__(self.widgets)
        self.pile.focus_position = 2
        self.selected_app_w = None
        self.handle_focus_changed()
        self.update_skip_rest_button()

    def selectable(self):
        return True

    def keypress(self, size, key):
        # handle keypress first, then get new focus widget
        rv = super().keypress(size, key)
        self.handle_focus_changed()
        return rv

    def handle_focus_changed(self):
        "Check if focused widget changed, then update readme."
        fw = self.pile.focus
        if not isinstance(fw, ApplicationWidget):
            return
        if fw != self.selected_app_w:
            self.selected_app_w = fw
            if fw is None:
                self.description_w.set_text("No selected application")
            else:
                self.metadata_controller.get_readme(
                    fw.application.csid.as_seriesname(),
                    partial(self._handle_readme_load, fw))

    def _handle_readme_load(self, fw, readme_f):
        if self.selected_app_w == fw:
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

    def build_widgets(self):
        ws = [Text("{} Applications in {}:".format(len(self.applications),
                                                   app.config['spell']))]
        max_app_name_len = max([len(a.service_name) for a in
                                self.applications])

        for a in self.applications:
            ws.append(Text(""))
            ws.append(ApplicationWidget(a, max_app_name_len,
                                        self.controller,
                                        self.do_deploy))

        self.description_w = Text("App description")
        ws += [HR(), self.description_w]

        self.skip_rest_button = PlainButton(
            "Deploy all",
            self.controller.do_deploy_remaining
        )
        cws = [('weight', 1, Text(" ")),
               (20, Color.button_secondary(
                   self.skip_rest_button,
                   focus_map='button_secondary focus'))]
        self.button_columns = Columns(cws, dividechars=1)

        ws += [HR(), self.button_columns]
        self.pile = Pile(ws)
        return Padding.center_90(Filler(self.pile, valign="top"))

    def do_deploy(self, application, sender):
        self.n_remaining -= 1
        self.update_skip_rest_button()
        self.selected_app_w.remove_buttons()

        self.controller.do_deploy(application,
                                  msg_cb=self.selected_app_w.set_progress)
        if self.n_remaining > 0:
            # find next available app widget to highlight. Start after
            # the current one and wrap around to top
            next_w = None
            reordered = self.pile.contents[self.pile.focus_position:] + \
                self.pile.contents[:self.pile.focus_position]
            for w, opts in reordered:
                if isinstance(w, ApplicationWidget) and w.selectable():
                    next_w = w
                    break
            ni = [w for w, _ in self.pile.contents].index(next_w)
            self.pile.focus_position = ni
        else:
            self.controller.finish()

    def update_skip_rest_button(self):
        t = "Deploy all {} Remaining Applications".format(
            self.n_remaining)
        self.skip_rest_button.set_label(t)
