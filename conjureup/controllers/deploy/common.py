import asyncio
from operator import attrgetter

from conjureup import events, juju, utils
from conjureup.app_config import app
from conjureup.models.step import StepModel


async def do_deploy(msg_cb):
    await events.ModelConnected.wait()
    cloud_types = juju.get_cloud_types_by_name()
    default_series = app.metadata_controller.series
    machines = app.metadata_controller.bundle.machines
    applications = sorted(app.metadata_controller.bundle.services,
                          key=attrgetter('service_name'))

    await pre_deploy(msg_cb=msg_cb)
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


async def pre_deploy(msg_cb):
    """ runs pre deploy script if exists
    """
    await events.ModelConnected.wait()

    # Set provider type for post-bootstrap
    app.env['JUJU_PROVIDERTYPE'] = app.juju.client.info.provider_type
    # Set current credential name (localhost doesn't have one)
    app.env['JUJU_CREDENTIAL'] = app.provider.credential or ''
    app.env['JUJU_CONTROLLER'] = app.provider.controller
    app.env['JUJU_MODEL'] = app.provider.model
    app.env['CONJURE_UP_SPELLSDIR'] = app.argv.spells_dir

    step = StepModel({},
                     filename='00_pre-deploy',
                     name='pre-deploy')
    await utils.run_step(step,
                         msg_cb)
    events.PreDeployComplete.set()


async def wait_for_applications(msg_cb):
    await events.DeploymentComplete.wait()
    msg = 'Waiting for deployment to settle.'
    app.log.info(msg)
    msg_cb(msg)

    step = StepModel({'title': 'Deployment Watcher'},
                     filename='00_deploy-done',
                     name='00_deploy-done')
    await utils.run_step(step, msg_cb)

    events.ModelSettled.set()
    msg = 'Model settled.'
    app.log.info(msg)
    msg_cb(msg)
