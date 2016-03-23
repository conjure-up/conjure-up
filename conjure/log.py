import logging
import logging.handlers


def setup_logging(app, debug=False):
    cmdslog = logging.handlers.SysLogHandler('/dev/log')
    if debug:
        env = 'DEBUG'
    else:
        env = 'INFO'
    cmdslog.setLevel(env)
    cmdslog.setFormatter(logging.Formatter(
        "[%(levelname)-4s: %(asctime)s, "
        "%(filename)s:%(lineno)d] %(message)s",
        datefmt='%m-%d %H:%M:%S'))

    logger = logging.getLogger(app)
    logger.setLevel(env)
    logger.addHandler(cmdslog)
    return logger
