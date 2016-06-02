from subprocess import run, PIPE
from conjure.app_config import app


def run_script(path):
    return run(path, shell=True, stderr=PIPE, stdout=PIPE, env=app.env)
