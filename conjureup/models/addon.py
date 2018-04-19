from itertools import chain
from pathlib import Path

import yaml

from conjureup.app_config import app
from conjureup.models.step import StepModel


class AddonModel:
    @classmethod
    def load_spell_addons(cls):
        """
        Return a list of all add-ons available for the current spell.
        """
        app.addons.clear()
        app.selected_addons.clear()
        addons_dir = Path(app.config['spell-dir']) / 'addons'
        for addon_path in sorted(addons_dir.glob('*')):
            if addon_path.is_dir():
                app.addons[addon_path.name] = AddonModel(addon_path.name)
        import ipdb
        ipdb.set_trace()

    @classmethod
    def selected_addons(cls):
        return [app.addons[name] for name in sorted(app.selected_addons)]

    @classmethod
    def selected_addons_steps(cls):
        return list(chain.from_iterable(
            addon.steps for addon in cls.selected_addons()))

    def __init__(self, name):
        self.name = name
        self.path = Path(app.config['spell-dir']) / 'addons' / name
        self.metadata = self._read('metadata.yaml')
        self.bundle = self._read('bundle.yaml')
        self.steps = [StepModel.load(step_path,
                                     source=self.friendly_name,
                                     addon_name=name)
                      for step_path in
                      sorted((self.path / 'steps').glob('*'))
                      if step_path.is_dir()]

    def _read(self, filename):
        filepath = self.path / filename
        if not filepath.exists():
            return {}
        return yaml.safe_load(filepath.read_text())

    @property
    def friendly_name(self):
        return self.metadata.get('friendly-name', self.name)

    @property
    def description(self):
        return self.metadata.get('description', self.name)
