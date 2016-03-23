import logging
from logging.handlers import SysLogHandler


def setup_logging(app, debug=False):
    cmdslog = SysLogHandler('/dev/log',
                            facility=SysLogHandler.LOG_DAEMON)
    if debug:
        env = logging.DEBUG
    else:
        env = logging.INFO
    cmdslog.setLevel(env)
    cmdslog.setFormatter(logging.Formatter(
        "%(name)s: [%(levelname)s]: %(message)s"))

    logger = logging.getLogger(app)
    logger.setLevel(env)
    logger.addHandler(cmdslog)
    return logger
