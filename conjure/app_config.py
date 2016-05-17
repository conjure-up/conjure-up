""" application config
"""
from types import SimpleNamespace


app = SimpleNamespace(
    ui=None,
    config=None,
    argv=None,
    controllers=None,
    current_model=None,
    current_controller=None,
    session_id=None,
    log=None,
    env=None,
    complete=False,
    headless=False)
