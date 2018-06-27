from operator import itemgetter

from ubuntui.utils import Padding
from ubuntui.widgets.hr import HR
from urwid import Text
from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.selectors import MenuSelectButtonList


class DestroyView(BaseView):
    title = "Destroy Deployment"
    subtitle = "Please choose a deployment to destroy"
    show_back_button = False

    def __init__(self, app, models, cb):
        self.app = app
        self.cb = cb
        self.controllers = models.keys()
        self.models = models
        self.config = self.app.config
        super().__init__()

    def _total_machines(self, model):
        """ Returns total machines in model
        """
        machines = model.get('machines', None)
        if machines is None:
            return 0
        return len(machines.keys())

    def build_widget(self):
        widget = MenuSelectButtonList()
        if len(self.controllers) > 0:
            widget.append(Text("Juju Controllers"))
            widget.append(HR())
            for controller in sorted(self.controllers):
                widget.append_option(controller)
                models = self.models[controller]['models']
                if len(models) > 0:
                    widget.append(Padding.line_break(""))
                    widget.append(Text("Juju Models"))
                    widget.append(HR())
                for model in sorted(models, key=itemgetter('name')):
                    widget.append_option(model['short-name'])
        widget.select_first()
        return widget

    def submit(self):
        if self.widget.selected:
            self.cb(self.widget.selected)
