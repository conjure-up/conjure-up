import yaml


class JujuModel:

    def __init__(self, meta):
        """ Init

        Arguments:
        meta: metadata from providers.json
        """
        self.meta = meta
        self.env = {}
        self.supports_placement = False

    def to_yaml(self):
        """ Outputs environment credentials to YAML
        """
        self.env['default'] = self.meta['name'].lower()
        self.env['environments'] = {
            self.meta['name'].lower(): {
                'type': self.meta['provider_type']
            }
        }

        sanitize_config = {k: v for k, v in self.meta['options'].items()
                           if v is not None}
        self.env['environments'][self.meta['name'].lower()].update(
            sanitize_config)
        return yaml.safe_dump(self.env, default_flow_style=False)
