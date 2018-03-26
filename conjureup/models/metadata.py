""" Spell metadata

This is the information found metadata.yaml in the
current spells top-level directory
"""
import yaml


class SpellMetadataException(Exception):
    pass


class SpellMetadata(dict):
    def __init__(self, metadata):
        super().__init__(metadata)

    @property
    def friendly_name(self):
        """ Human Friendly Name of spell
        """
        return self.get('friendly-name', 'Unknown')

    @property
    def version(self):
        """ Spell version
        """
        return self.get('version', 1)

    @property
    def bundle_name(self):
        """ Name of charmstore bundle
        """
        return self.get('bundle-name', None)

    @property
    def options_whitelist(self):
        """ List of options to display by default
        """
        return self.get('options-whitelist', {})

    @property
    def cloud_whitelist(self):
        """ returns list of approved providers for spell
        """
        return self.get('cloud-whitelist', [])

    @property
    def cloud_blacklist(self):
        """ returns list of non-approved providers for spell
        """
        return self.get('cloud-blacklist', [])

    @classmethod
    def load(cls, path):
        """ Load spell metadata
        """
        if path.exists():
            return SpellMetadata(
                yaml.safe_load(path.read_text()))
        raise SpellMetadataException("Unable to parse spell metadata.")
