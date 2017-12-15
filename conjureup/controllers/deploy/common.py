import asyncio
from operator import attrgetter

from conjureup import consts, events, juju
from conjureup.app_config import app


def _parse_placement(spec):
    if not spec:
        machine = None
        container_type = None
        container_num = None
    elif '/' in spec:
        machine, container_type, container_num = spec.split('/')
    elif ':' in spec:
        machine, container_type = reversed(spec.split(':'))
        container_num = None
    elif spec.isdigit():
        machine = spec
        container_type = None
        container_num = None
    else:
        machine = None
        container_type = spec
        container_num = None
    return machine, container_type, container_num


def _format_placement(machine, container_type, container_num):
    if machine is None and container_type is None:
        return None
    elif machine is None:
        return container_type
    elif container_type is None:
        return machine
    elif container_num is None:
        return ':'.join([container_type, machine])
    else:
        return '/'.join([machine, container_type, container_num])


async def do_deploy(msg_cb):
    await events.ModelConnected.wait()
    cloud_types = juju.get_cloud_types_by_name()
    default_series = app.metadata_controller.series
    machines = app.metadata_controller.bundle.machines
    applications = sorted(app.metadata_controller.bundle.services,
                          key=attrgetter('service_name'))
    is_localhost = cloud_types[app.provider.cloud] == consts.cloud_types.LOCAL

    for step in app.steps:
        await step.before_deploy(msg_cb=msg_cb)
    events.PreDeployComplete.set()

    # FIXME: This whole section is super dumb and we should really just pass
    # the bundle to Juju.  This is mostly to support MAAS machine pinning,
    # but we should be able to come up with a better solution.
    if is_localhost:
        # for localhost, just ignore placement altogether
        for service in applications:
            service.placement_spec = None
    else:
        # for non-localhost, we pre-deploy the machines, so we have to do
        # a bunch of manipulation of the placement and constraints
        placements = {
            service.service_name: [_parse_placement(spec)
                                   for spec in service.placement_spec or []]
            for service in applications
        }

        # copy constraints over to machines prior to pre-allocating
        # (See https://github.com/conjure-up/conjure-up/issues/1272)
        for service in applications:
            if not service.constraints:
                continue
            for m, _, _ in placements[service.service_name]:
                if m not in machines:
                    continue
                machines[m]['constraints'] = service.constraints

        # pre-allocate machines
        machine_map = await juju.add_machines(applications,
                                              machines,
                                              msg_cb=msg_cb)

        # remap placement specs to pre-allocated machines
        for service in applications:
            new_placements = []
            for m, c_type, c_num in placements[service.service_name]:
                if m in machine_map:
                    m = machine_map[m]
                spec = _format_placement(m, c_type, c_num)
                if spec:
                    new_placements.append(spec)
            service.placement_spec = new_placements

    tasks = []
    for service in applications:
        tasks.extend([
            juju.deploy_service(service, default_series, msg_cb=msg_cb),
            juju.set_relations(service, msg_cb=msg_cb),
        ])
    await asyncio.gather(*tasks)
    events.DeploymentComplete.set()


async def wait_for_applications(msg_cb):
    await events.DeploymentComplete.wait()

    for step in app.steps:
        await step.before_wait(msg_cb=msg_cb)

    msg = 'Waiting for deployment to settle.'
    app.log.info(msg)
    msg_cb(msg)

    await juju.wait_for_deployment()

    events.ModelSettled.set()
    msg = 'Model settled.'
    app.log.info(msg)
    msg_cb(msg)
