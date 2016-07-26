import logging
from logging.handlers import SysLogHandler


def setup_logging(app, debug=False):
    cmdslog = SysLogHandler('/dev/log',
                            facility=SysLogHandler.LOG_DAEMON)
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
    return logger
