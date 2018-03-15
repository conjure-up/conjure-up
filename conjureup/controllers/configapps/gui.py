import asyncio

from conjureup import controllers, events, juju
from conjureup.app_config import app
from conjureup.consts import cloud_types
from conjureup.maas import setup_maas
from conjureup.ui.views.applicationconfigure import ApplicationConfigureView
from conjureup.ui.views.applicationlist import ApplicationListView


class ConfigAppsController:

    def __init__(self):
        self.applications = []
        self.maas_machine_map = {}

    def do_configure(self, application):
        "shows configure view for application"
        cv = ApplicationConfigureView(application,
                                      lambda: self.render(going_back=True))
        cv.show()

    async def get_maas_constraints(self, machine_id):
        if machine_id not in self.maas_machine_map:
            return ''
        maas_machine = self.maas_machine_map[machine_id]
        await app.loop.run_in_executor(
            None, app.maas.client.assign_id_tags, [maas_machine])
        machine_tag = maas_machine.instance_id.split('/')[-2]
        return "tags={}".format(machine_tag)

    async def connect_maas(self):
        """Try to init maas client.
        loops until we get an unexpected exception or we succeed.
        """
        n = 30
        while True:
            try:
                await app.loop.run_in_executor(None, setup_maas)
            except juju.ControllerNotFoundException as e:
                await asyncio.sleep(1)
                n -= 1
                if n == 0:
                    raise e
                continue
            else:
                events.MAASConnected.set()
                break

    def finish(self):
        return controllers.use('bootstrap').render()

    def render(self, going_back=False):
        if going_back:
            # coming back from config or architecture view
            self.list_view.update_units()
            self.list_view.show()
            return

        if app.provider.cloud_type == cloud_types.MAAS:
            app.loop.create_task(self.connect_maas())

        self.list_view = ApplicationListView(app.current_bundle.applications,
                                             self.do_configure,
                                             self.finish,
                                             self.back)
        self.list_view.show()

    def back(self):
        controllers.use('showsteps').render(going_back=True)


_controller_class = ConfigAppsController
