from conjureup import controllers, events, juju, utils
from conjureup.app_config import app

from . import common


class NewCloudController:
    def render(self):
        creds = None
        cloud_type = juju.get_cloud_types_by_name()[app.current_cloud]
        if cloud_type != 'localhost':
            creds = common.try_get_creds(app.current_cloud)
            if not creds:
                utils.warning("You attempted to do an install against a cloud "
                              "that requires credentials that could not be "
                              "found.  If you wish to supply those "
                              "credentials please run "
                              "`juju add-credential "
                              "{}`.".format(app.current_cloud))
                events.Shutdown.set(1)
                return

        if cloud_type == 'localhost':
            # Grab list of available physical networks to bind our bridge to
            iface = None
            try:
                ifaces = utils.get_physical_network_interfaces()
                # Grab a physical network device that has an ip address
                iface = [i for i in ifaces
                         if utils.get_physical_network_ipaddr(i)][0]
            except Exception:
                utils.warning(
                    "Could not find a suitable physical network interface "
                    "to create a LXD bridge on. Please check your network "
                    "configuration.")
                events.Shutdown.set(1)

            if not common.get_lxd_setup_path().exists():
                common.lxd_init(iface)
                common.get_lxd_setup_path().touch()

        app.loop.create_task(self.finish(creds))

    async def finish(self, creds):
        await common.do_bootstrap(creds,
                                  msg_cb=utils.info,
                                  fail_msg_cb=utils.error)
        controllers.use('deploy').render()


_controller_class = NewCloudController
