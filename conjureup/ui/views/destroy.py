from conjureup.ui.views.base import BaseView
from conjureup.ui.widgets.selectors import MenuSelectButtonList


class DestroyView(BaseView):
    title = "Destroy Deployment"
    subtitle = "Please choose a deployment to destroy"
    show_back_button = False

    def __init__(self, app, deployed_map, show_snaps, cb):
        self.app = app
        self.cb = cb
        self.deployed_map = deployed_map
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
        if self.deployed_map:
            for name, deploy in self.deployed_map.items():
                value_map = {
                    'type': 'juju',
                    'cloud': deploy['controller']['cloud'],
                    'controller': name
                }
                widget.append_option(
                    label="{} ({})".format(
                        name,
                        deploy['controller']['cloud']),
                    value=value_map)
                for model in deploy['models']:
                    if model['name'] == 'admin/controller':
                        continue
                    value_map['model'] = model['short-name']
                    widget.append_option(
                        label="- {}".format(
                            model['short-name']),
                        value=value_map)
        if self.show_snaps:
            value_map = {
                'type': 'snap',
                'snap': 'microk8s'
            }
            widget.append_option(label='microk8s (localhost)',
                                 value=value_map)
        widget.select_first()
        return widget

    def submit(self):
        if self.widget.selected:
            self.cb(self.widget.selected)
