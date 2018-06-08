import asyncio
from operator import attrgetter

from conjureup import controllers, events
from conjureup.app_config import app
from conjureup.ui.views.deploystatus import DeployStatusView

from . import common


class DeployController:
    def render(self):
        """ Render deploy status view
        """
        view = DeployStatusView()
        view.show()

        app.loop.create_task(common.do_deploy(view.set_footer))
        app.loop.create_task(self._refresh(view))
        app.loop.create_task(self._wait_for_applications(view))

    async def _refresh(self, view):
        applications = sorted(app.current_bundle.applications,
                              key=attrgetter('name'))
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
            view_data[service.name] = {'units': units}
            # always visible, even if they're not in the model yet
            name = '{}/{}'.format(service.name, 0)
            public_address = ''
            machine = ''
            agent_status = 'installing'
            agent_info = ''
            workload_status = 'installing'
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
