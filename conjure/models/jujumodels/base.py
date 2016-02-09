import yaml


class JujuModel:

    name = None
    provider_type = None
    description = None
    env = {}
    config = {}

    # Does the inherited model support placing
    # services on specific machines?
    supports_placement = False

    @classmethod
    def to_yaml(cls):
        """ Outputs environment credentials to YAML
        """
        cls.env['default'] = cls.name.lower()
        cls.env['environments'] = {
            cls.name.lower(): {
                'type': cls.provider_type
            }
        }

        sanitize_config = {k: v for k, v in cls.config.items()
                           if v is not None}
        cls.env['environments'][cls.name.lower()].update(sanitize_config)
        return yaml.safe_dump(cls.env, default_flow_style=False)
