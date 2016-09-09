import logging
from logging.handlers import TimedRotatingFileHandler

try:
    from systemd.journal import JournalHandler
except ImportError:
    from systemd.journal import JournalLogHandler as JournalHandler


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
    logger.addHandler(JournalHandler(SYSLOG_IDENTIFIER=app))

    return logger
