from pathlib import Path

from conjureup.app_config import app


def save_step_results():
    results_file = Path(app.config['spell-dir']) / 'results.txt'
    results_file.write_text(''.join([
        "{}: {}\n".format(step.title, step.result) for step in app.steps
    ]))
