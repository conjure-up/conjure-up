from conjureup import controllers, events, juju, utils
from conjureup.app_config import app

from . import common


class NewCloudController:
    def render(self):
        creds = None
        app.env['JUJU_PROVIDERTYPE'] = \
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

        # LXD is a special case as we want to make sure a bridge
        # is configured. If not we'll bring up a new view to allow
        # a user to configure a LXD bridge with suggested network
        # information.
        if cloud_type == 'localhost':
            lxd = common.is_lxd_ready()
            if not lxd['ready']:
                return controllers.use('lxdsetup').render(lxd['msg'])

        app.loop.create_task(self.finish(creds))

    async def finish(self, creds):
        await common.do_bootstrap(creds,
                                  msg_cb=utils.info,
                                  fail_msg_cb=utils.error)
        controllers.use('deploy').render()


_controller_class = NewCloudController
