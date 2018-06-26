from functools import partial
from operator import itemgetter

from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import menu_btn
from urwid import Filler, Pile, Text
from conjureup.ui.views.base import BaseView


class DestroyView(BaseView):
    title = "Destroy Deployment"
    subtitle = "Please choose a deployment to destroy"

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
        total_items = []
        for controller in sorted(self.controllers):
            models = self.models[controller]['models']
            if len(models) > 0:
                total_items.append(Color.label(
                    Text("{} ({})".format(controller,
                                          models[0].get('cloud', "")))
                ))
                for model in sorted(models, key=itemgetter('name')):
                    if model['name'] == "controller":
                        continue
                    if model['life'] == 'dying':
                        continue

                    label = "  {}, Machine Count: {}{}".format(
                        model['name'],
                        self._total_machines(model),
                        ", Running since: {}".format(
                            model['status'].get('since'))
                        if 'since' in model['status'] else '')
                    total_items.append(
                        Color.body(
                            menu_btn(label=label,
                                     on_press=partial(self.submit,
                                                      controller,
                                                      model)),
                            focus_map='menu_button focus'
                        ))
                total_items.append(Padding.line_break(""))
            total_items.append(Padding.line_break(""))
        return Padding.center_80(Filler(Pile(total_items), valign='top'))

    def submit(self, controller, model, btn):
        self.cb(controller, model)

    def cancel(self, btn):
        EventLoop.exit(0)
