import asyncio
from operator import attrgetter

from conjureup import controllers, events
from conjureup.app_config import app
from conjureup.telemetry import track_screen
from conjureup.ui.views.deploystatus import DeployStatusView

from . import common


class DeployController:
    def render(self):
        """ Render deploy status view
        """
        track_screen("Deploy")
        view = DeployStatusView()
        view.show()

        app.loop.create_task(common.do_deploy(view.set_footer))
        app.loop.create_task(self._refresh(view))
        app.loop.create_task(self._wait_for_applications(view))

    async def _refresh(self, view):
        applications = sorted(app.metadata_controller.bundle.services,
                              key=attrgetter('service_name'))
        await events.ModelConnected.wait()
        while not events.ModelSettled.is_set():
            if events.Error.is_set():
                # deploy or wait_for_apps task failed, so stop refreshing
                # (the error screen will be shown instead)
                return
            view.refresh_nodes(self._build_view_data(applications))
            await asyncio.sleep(1)

    def _build_view_data(self, applications):
        view_data = {}
        for service in applications:
            units = {}
            view_data[service.service_name] = {'units': units}
            num_units = service.num_units
            if service.service_name in app.juju.client.applications:
                juju_app = app.juju.client.applications[service.service_name]
                num_units = max(service.num_units, len(juju_app.units))
            else:
                juju_app = None
            for unit_num in range(num_units):
                if juju_app and len(juju_app.units) > unit_num:
                    unit = juju_app.units[unit_num]
                    name = unit.name
                    public_address = unit.public_address
                    machine = unit.machine_id
                    agent_status = unit.agent_status
                    agent_info = unit.agent_status_message
                    workload_status = unit.workload_status
                    workload_info = unit.workload_status_message
                else:
                    # fill out with placeholder so that the units are
                    # always visible, even if they're not in the model yet
                    name = '{}/{}'.format(service.service_name, unit_num)
                    public_address = ''
                    machine = ''
                    agent_status = ''
                    agent_info = ''
                    workload_status = ''
                    workload_info = ''
                units.update({
                    name: {
                        'public-address': public_address,
                        'machine': machine,
                        'agent-status': {
                            'status': agent_status,
                            'info': agent_info,
                        },
                        'workload-status': {
                            'status': workload_status,
                            'info': workload_info,
                        },
                    }
                })
        return view_data

    async def _wait_for_applications(self, view):
        await common.wait_for_applications(view.set_footer)
        controllers.use('runsteps').render()


_controller_class = DeployController
