from collections import OrderedDict

from conjureup import controllers, events, utils
from conjureup.app_config import app
from conjureup.controllers.steps import common


class StepsController:
    def render(self):
        app.loop.create_task(self.do_steps())

    async def do_steps(self):
        step_metas = common.get_step_metadata_filenames()
        results = OrderedDict()
        for step_meta_path in step_metas:
            step_model = common.load_step(step_meta_path)
            if utils.is_linux():
                if step_model.needs_sudo and not utils.can_sudo():
                    utils.error("Step requires passwordless sudo: {}".format(
                        step_model.title))
                    events.Shutdown.set(1)
                    return
            results[step_model.title] = await common.do_step(step_model,
                                                             utils.info)
        events.PostDeployComplete.set()
        return controllers.use('summary').render(results)


_controller_class = StepsController
