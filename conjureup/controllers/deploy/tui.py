import asyncio
from operator import attrgetter

from conjureup import controllers, events, juju, utils
from conjureup.app_config import app

from . import common


class DeployController:
    def render(self):
        app.loop.create_task(self.do_deploy())

    async def do_deploy(self):
        cloud_types = juju.get_cloud_types_by_name()
        default_series = app.metadata_controller.series
        machines = app.metadata_controller.bundle.machines
        applications = sorted(app.metadata_controller.bundle.services,
                              key=attrgetter('service_name'))

        if not events.Bootstrapped.is_set():
            controllers.use('bootstrap').render()

        await common.pre_deploy(msg_cb=utils.info)
        await juju.add_model(app.current_model,
                             app.current_controller,
                             app.current_cloud)
        await juju.add_machines(applications,
                                machines,
                                msg_cb=utils.info)
        tasks = []
        for service in applications:
            # ignore placement when deploying to localhost
            if cloud_types[app.current_cloud] == "localhost":
                service.placement_spec = None
            tasks.append(juju.deploy_service(service, default_series,
                                             msg_cb=utils.info))
            tasks.append(juju.set_relations(service,
                                            msg_cb=utils.info))
        await asyncio.gather(*tasks)
        events.DeploymentComplete.set()
        controllers.use('deploystatus').render()


_controller_class = DeployController
