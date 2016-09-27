# Copyright 2014-2016 Canonical, Ltd.
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

""" Logging interface
"""

from __future__ import unicode_literals

import logging
import os
import pprint
from logging.handlers import TimedRotatingFileHandler


class PrettyLog():

    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        return pprint.pformat(self.obj)


def setup_logger(name=__name__, cfg_path='.'):
    """setup logging

    """
    if not os.path.isdir(cfg_path):
        os.makedirs(cfg_path)
    LOGFILE = os.path.join(cfg_path, 'placement.log')
    commandslog = TimedRotatingFileHandler(LOGFILE,
                                           when='D',
                                           interval=1,
                                           backupCount=7)

    commandslog.setLevel('DEBUG')
    commandslog.setFormatter(logging.Formatter(
        "[%(levelname)-4s: %(asctime)s, "
        "%(filename)s:%(lineno)d] %(message)s",
        datefmt='%m-%d %H:%M:%S'))

    logger = logging.getLogger('')
    logger.setLevel('DEBUG')

    no_filter = os.environ.get('PLACEMENT_NOFILTER', None)
    if no_filter is None:
        f = logging.Filter(name='bundleplacer')
        commandslog.addFilter(f)

    logger.addHandler(commandslog)

    return logger
