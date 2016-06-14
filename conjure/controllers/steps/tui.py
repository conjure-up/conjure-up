from conjure import controllers


def finish():
    """ We can't really process interactive steps in headless mode. Bypass
    for now.
    """
    return controllers.use('summary').render([])


def render():
    finish()
