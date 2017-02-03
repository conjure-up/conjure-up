import logging
import os
import stat
from logging.handlers import SysLogHandler, TimedRotatingFileHandler


class _log:

    def __init__(self, app, logger):
        self.app = app
        self.logger = logger

    def debug(self, msg):
        self.logger.debug("{}: {}".format(self.app, msg))

    def error(self, msg):
        self.logger.error("{}: {}".format(self.app, msg))

    def info(self, msg):
        self.logger.info("{}: {}".format(self.app, msg))

    def exception(self, msg):
        self.logger.exception("{}: {}".format(self.app, msg))

    def warning(self, msg):
        self.logger.warning("{}: {}".format(self.app, msg))


def setup_logging(app, logfile, debug=True):
    cmdslog = TimedRotatingFileHandler(logfile,
                                       when='D',
                                       interval=1,
                                       backupCount=7)

    if debug:
        env = logging.DEBUG
        cmdslog.setFormatter(logging.Formatter(
            "%(asctime)s %(name)s: [%(levelname)s] "
            "%(filename)s:%(lineno)d - %(message)s"))
    else:
        env = logging.INFO
        cmdslog.setFormatter(logging.Formatter(
            "%(asctime)s %(name)s: [%(levelname)s] %(message)s"))

    cmdslog.setLevel(env)

    logger = logging.getLogger(app)
    logger.setLevel(env)
    logger.addHandler(cmdslog)
    if os.path.exists('/dev/log'):
        st_mode = os.stat('/dev/log').st_mode
        if stat.S_ISSOCK(st_mode):
            syslog_h = SysLogHandler(address='/dev/log')
            syslog_h.set_name(app)
            logger.addHandler(syslog_h)

    return _log(app, logger)
