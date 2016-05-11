""" Service walkthrough widget
"""
import logging

from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.input import IntegerEditor
from urwid import connect_signal, Divider, WidgetWrap, Text, Padding, Pile

log = logging.getLogger('service_walkthrough')
import q

class ServiceWalkthroughWidget(WidgetWrap):
    def __init__(self, service, metadata_controller,
                 deploy_controller):
        self.service = service
        self.metadata_controller = metadata_controller
        self.deploy_controller = deploy_controller
        self.is_selected = False
        self.is_deployed = False
        w = self.build_widgets()
        super().__init__(w)

    def selectable(self):
        return True
        
    def build_widgets(self):
        self.title = Text(self.service.service_name)
        self.description_w = Text("Description Loading…")
        self.metadata_controller.get_charm_info(
            self.service.csid.as_str_without_rev(),
            self.handle_info_updated)

        self.scale_edit = IntegerEditor(caption="Scale", default=1)
        connect_signal(self.scale_edit._edit, 'change',
                       self.handle_scale_changed)
        self.continue_button = PlainButton("Make it so", self.do_deploy)
        ws = [self.title,
              Padding(self.description_w, left=2),
              Divider()]
        self.pile = Pile(ws)
        return self.pile

    def handle_info_updated(self, new_info):
        self.description_w.set_text(new_info["Meta"]["charm-metadata"]["Summary"])
        self.update()

    def _set_pile(self, ws):
        opts = self.pile.options()
        self.pile.contents[2:-1] = [(w, opts) for w in ws]
        
    def update_deployed(self):
        self._set_pile([])

    def update_selected_undeployed(self):
        self._set_pile([Padding(self.scale_edit, align='right', width='pack'),
                        Padding(self.continue_button, align='right', width='pack')])
        
    def update(self):
        if self.is_deployed:
            self.update_deployed()
        elif self.is_selected:
            self.update_selected_undeployed()
        else:
            self._set_pile([])

    @q.t
    def set_selected(self, now_selected):
        if self.is_deployed:
            return
        self.is_selected = now_selected
        if now_selected:
            self.update_selected_undeployed()
            self.pile.selected_index = 4

        q.q(self.pile.selected_index)
        q.q(self.pile.contents)
        
    def handle_scale_changed(self, sender, value):
        self.deploy_controller.handle_service_scale_change(self.service, value)

    def do_deploy(self, sender):
        self.deploy_controller.handle_service_deploy(self.service)
        self.is_deployed = True
