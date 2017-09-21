import asyncio
from operator import attrgetter

from conjureup import events, juju
from conjureup.app_config import app
from conjureup.models.step import StepModel


async def do_deploy(msg_cb):
    await events.ModelConnected.wait()
    cloud_types = juju.get_cloud_types_by_name()
    default_series = app.metadata_controller.series
    machines = app.metadata_controller.bundle.machines
    applications = sorted(app.metadata_controller.bundle.services,
                          key=attrgetter('service_name'))

    step = StepModel({}, name='before-deploy')
    await step.before_deploy(msg_cb=msg_cb)
    events.PreDeployComplete.set()

    machine_map = await juju.add_machines(applications,
                                          machines,
                                          msg_cb=msg_cb)
    tasks = []
    for service in applications:
        if cloud_types[app.provider.cloud] == "localhost":
            # ignore placement when deploying to localhost
            service.placement_spec = None
        elif service.placement_spec:
            # remap machine references to actual deployed machine IDs
            # (they will only ever not already match if deploying to
            # an existing model that has other machines)
            new_placements = []
            for plabel in service.placement_spec:
                if ':' in plabel:
                    ptype, pid = plabel.split(':')
                    new_placements.append(':'.join([ptype, machine_map[pid]]))
                else:
                    new_placements.append(machine_map[plabel])
            service.placement_spec = new_placements

        tasks.append(juju.deploy_service(service, default_series,
                                         msg_cb=msg_cb))
        tasks.append(juju.set_relations(service,
                                        msg_cb=msg_cb))
    await asyncio.gather(*tasks)
    events.DeploymentComplete.set()


async def wait_for_applications(msg_cb):
    await events.DeploymentComplete.wait()
    msg = 'Waiting for deployment to settle.'
    app.log.info(msg)
    msg_cb(msg)

    await juju.wait_for_deployment()

    events.ModelSettled.set()
    msg = 'Model settled.'
    app.log.info(msg)
    msg_cb(msg)
