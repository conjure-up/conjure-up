
from functools import partial

import requests

from conjureup import __version__ as VERSION
from conjureup.app_config import app
from conjureup.async import submit

GA_ID = "UA-1018242-61"
TELEMETRY_ASYNC_QUEUE = "telemetry-async-queue"


def track_screen(screen_name):
    if app.argv.debug or app.argv.notrack:
        return
    args = dict(cd=screen_name,
                t="screenview")
    if 'spell' in app.config:
        args['cd1'] = app.config['spell']

    submit(partial(_post_track, args), lambda _: None,
           queue_name=TELEMETRY_ASYNC_QUEUE)


def track_event(category, action, label):
    ""
    if app.argv.debug or app.argv.notrack:
        return
    args = dict(ec=category,
                ea=action,
                el=label,
                t='event')
    if 'spell' in app.config:
        args['cd1'] = app.config['spell']
    submit(partial(_post_track, args), lambda _: None,
           queue_name=TELEMETRY_ASYNC_QUEUE)


def track_exception(description, is_fatal=True):
    ""
    if app.argv.debug or app.argv.notrack:
        return
    exf = 1 if is_fatal else 0
    args = dict(t='exception',
                exd=description,
                exf=exf)
    if 'spell' in app.config:
        args['cd1'] = app.config['spell']
    submit(partial(_post_track, args), lambda _: None,
           queue_name=TELEMETRY_ASYNC_QUEUE)


def _post_track(arg_dict):
    params = dict(tid=GA_ID, v=1, aip=1, ds='app', cid=app.session_id,
                  av=VERSION, an="Conjure-Up")

    params.update(arg_dict)
    requests.post("http://www.google-analytics.com/collect",
                  data=params)
