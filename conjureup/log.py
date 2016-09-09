import logging
import os
import stat
from logging.handlers import SysLogHandler, TimedRotatingFileHandler


def setup_logging(app, logfile, debug=False):
    cmdslog = TimedRotatingFileHandler(logfile,
                                       when='D',
                                       interval=1,
                                       backupCount=7)
    if debug:
        env = logging.DEBUG
        cmdslog.setFormatter(logging.Formatter(
            "%(name)s: [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"))
    else:
        env = logging.INFO
        cmdslog.setFormatter(logging.Formatter(
            "%(name)s: [%(levelname)s] %(message)s"))

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

    return logger
