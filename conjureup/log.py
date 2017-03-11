import logging
import os
import stat
from logging.handlers import SysLogHandler, TimedRotatingFileHandler

from conjureup import consts


def setup_logging(app, logfile, debug=True):
    old_factory = logging.getLogRecordFactory()

    def spell_record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        if record.name != 'conjure-up':
            record.filename = '{}: {}'.format(record.name, record.filename)
        spell_name = app.config.get('spell', consts.UNSPECIFIED_SPELL)
        record.name = 'conjure-up/{}'.format(spell_name)
        return record

    logging.setLogRecordFactory(spell_record_factory)

    cmdslog = TimedRotatingFileHandler(logfile,
                                       when='D',
                                       interval=1,
                                       backupCount=7)
    cmdslog.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - "
        "%(filename)s:%(lineno)d - %(message)s"))

    root_logger = logging.getLogger()
    app_logger = logging.getLogger('conjure-up')

    if debug:
        app_logger.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.DEBUG)
    else:
        # always use DEBUG level for app, for now
        app_logger.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.INFO)

    root_logger.addHandler(cmdslog)
    if os.path.exists('/dev/log'):
        st_mode = os.stat('/dev/log').st_mode
        if stat.S_ISSOCK(st_mode):
            syslog_h = SysLogHandler(address='/dev/log')
            syslog_h.set_name('conjure-up')
            app_logger.addHandler(syslog_h)

    return app_logger
