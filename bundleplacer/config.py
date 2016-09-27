# -*- mode: python; -*-
#
# Copyright 2015 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import logging
import os

import yaml

log = logging.getLogger('bundleplacer')


class ConfigException(Exception):
    pass


class Config:

    def __init__(self, name, cfg_obj=None, save_backups=True):
        self.name = name
        if cfg_obj is None:
            self._config = {}
        else:
            self._config = cfg_obj
        self.save_backups = save_backups

    def save(self):
        """ Saves configuration """
        try:
            if not os.path.exists(self.cfg_path):
                os.makedirs(self.cfg_path)
            if self.save_backups and os.path.exists(self.cfg_file):
                datestr = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
                backup_path = os.path.join(self.cfg_path, "config-backups")
                backupfilename = "{}/config-{}.yaml".format(backup_path,
                                                            datestr)
                os.makedirs(backup_path, exist_ok=True)
                os.rename(self.cfg_file, backupfilename)
            with open(self.cfg_file, 'w') as f:
                f.write(yaml.safe_dump(dict(self._config),
                                       default_flow_style=False))
        except IOError as e:
            raise ConfigException("Unable to save configuration: {}".format(e))

    @property
    def cfg_path(self):
        """ top level configuration path """
        fn = '~/.config/{}'.format(self.name)
        return os.path.expanduser(fn)

    @property
    def cfg_file(self):
        return os.path.join(self.cfg_path, 'config.yaml')

    @classmethod
    def share_path(cls):
        """ Application share path
        """
        return "/usr/share/bundle-placer/share"

    def setopt(self, key, val):
        """ sets config option """
        try:
            self._config[key] = val
            self.save()
        except Exception as e:
            log.exception("Failed to set {} in config: {}".format(key, e))

    def getopt(self, key):
        if key in self._config:
            return self._config[key]
        else:
            if hasattr(self, key):
                attr = getattr(self, key)
                return attr() if callable(attr) else attr
            return False
