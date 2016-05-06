""" Service walkthrough widget
"""
import logging
from ubuntui.widgets.input import IntegerEditor
from urwid import connect_signal, Divider, WidgetWrap, Text, Padding, Pile

log = logging.getLogger('service_walkthrough')


class ServiceWalkthroughWidget(WidgetWrap):
    def __init__(self, service, metadata_controller, scale_cb,
                 ctype_cb):
        self.service = service
        self.metadata_controller = metadata_controller
        self.scale_cb = scale_cb
        self.ctype_cb = ctype_cb
        w = self.build_widgets()
        super().__init__(w)

    def build_widgets(self):
        self.title = Text(self.service.service_name)
        self.description_w = Text("")
        self.scale_edit = IntegerEditor(caption="Scale", default=1)
        connect_signal(self.scale_edit._edit, 'change',
                       self.handle_scale_changed)
        ws = [self.title,
              Padding(self.description_w, left=2),
              Padding(self.scale_edit, align='right', width='pack'),
              Divider()]
        return Pile(ws)

    def handle_info_updated(self, new_info):
        self.update()
    
    def update(self):
        info = self.metadata_controller.get_charm_info(
            self.service.csid.as_str_without_rev(),
            self.handle_info_updated)
        if info:
            self.description_w.set_text(info["Meta"]["charm-metadata"]["Summary"])
    
    def handle_scale_changed(self, sender, value):
        self.scale_cb(self.service, value)
