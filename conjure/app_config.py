""" application config
"""
from types import SimpleNamespace


app = SimpleNamespace(

    # The conjure-up UI framework
    ui=None,

    # Contains metadata and spell name
    config=None,

    # cli opts
    argv=None,

    # Current Juju model being used
    current_model=None,

    # Current Juju controller selected
    current_controller=None,

    # Session ID for current deployment
    session_id=None,

    # Application logger
    log=None,

    # Application environment passed to processing steps
    env=None,

    # Did deployment complete
    complete=False,

    # Run in non interactive mode
    headless=False,

    # Remote endpoint type, vcs, charmstore, charmstore-direct, direct
    fetcher=None)
