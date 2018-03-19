from conjureup import utils
from conjureup.app_config import app


async def run_before_config(msg_cb, done_cb):
    for step in app.all_steps:
        if not step.has_before_config:
            continue
        await step.before_config(msg_cb)
    if app.has_bundle_modifications:
        utils.setup_metadata_controller()
    done_cb()
