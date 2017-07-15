import sys

from prettytable import PrettyTable
from termcolor import colored

from conjureup import events, utils
from conjureup.app_config import app

from . import common


class RunStepsController:
    def render(self):
        app.loop.create_task(self.run_steps())

    async def run_steps(self):
        utils.info("Running post-deployment steps")
        for step in app.steps:
            step.result = await common.do_step(step, utils.info)

        common.save_step_results()
        self.show_summary()

        utils.info("Installation of your big software is now complete.")
        events.PostDeployComplete.set()
        events.Shutdown.set(0)

    def show_summary(self):
        utils.info("Post-Deployment Step Results")
        table = PrettyTable()
        table.field_names = ["Application", "Result"]
        for step in app.steps:
            table.add_row(self._format_step_result(step))
        print(table)

    def _format_step_result(self, step):
        if sys.__stdin__.isatty():
            return [colored(step.title, 'blue', attrs=['bold']),
                    colored(step.result, 'green', attrs=['bold'])]
        else:
            return [step.title, step.result]


_controller_class = RunStepsController
