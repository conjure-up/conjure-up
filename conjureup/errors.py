from conjureup.app_config import app
from conjureup.telemetry import track_exception


def handle_exception(exc):
    track_exception(exc.args[0])
    return app.ui.show_exception_message(exc)
