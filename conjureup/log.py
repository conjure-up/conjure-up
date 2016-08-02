import logging
from logging.handlers import TimedRotatingFileHandler


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
    return logger
