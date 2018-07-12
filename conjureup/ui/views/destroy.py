from operator import itemgetter

from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.selectors import MenuSelectButtonList


class DestroyView(BaseView):
    title = "Destroy Deployment"
    subtitle = "Please choose a deployment to destroy"
    show_back_button = False

    def __init__(self, app, models, show_snaps, cb):
        self.app = app
        self.cb = cb
        self.controllers = models.keys()
        self.models = models
        self.show_snaps = show_snaps
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
            for controller in sorted(self.controllers):
                models = self.models[controller]['models']
                for model in sorted(models, key=itemgetter('name')):
                    if model['name'] == 'admin/controller':
                        continue
                    widget.append_option(
                        label="{} ({})".format(
                            model['name'],
                            model['cloud']),
                        value=model['short-name'])
        if self.show_snaps:
            widget.append_option(label='microk8s (localhost)',
                                 value='microk8s')
        widget.select_first()
        return widget

    def submit(self):
        if self.widget.selected:
            self.cb(self.widget.selected)
