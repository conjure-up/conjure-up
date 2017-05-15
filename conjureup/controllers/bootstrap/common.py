import os

from conjureup import controllers, juju, utils
from conjureup.app_config import app
from conjureup.telemetry import track_event


class BootstrapController:
    def __init__(self, msg_cb):
        self.msg_cb = msg_cb

    def render(self):
        app.loop.create_task(self.do_bootstrap(app.current_credential))
        controllers.use('deploy').render()

    async def do_bootstrap(self, creds):
        if app.current_controller is None:
            app.current_controller = "conjure-up-{}-{}".format(
                app.current_cloud,
                utils.gen_hash())

        if app.current_model is None:
            app.current_model = utils.gen_model()

        if not app.is_jaas:
            await self.pre_bootstrap()
            app.log.info('Bootstrapping Juju controller.')
            self.msg_cb('Bootstrapping Juju controller.')
            track_event("Juju Bootstrap", "Started", "")
            cloud_with_region = app.current_cloud
            if app.current_region:
                cloud_with_region = '/'.join([app.current_cloud,
                                              app.current_region])
            success = await juju.bootstrap(app.current_controller,
                                           cloud_with_region,
                                           app.current_model,
                                           credential=creds)
            if not success:
                pathbase = os.path.join(
                    app.config['spell-dir'],
                    '{}-bootstrap').format(app.current_controller)
                with open(pathbase + ".err") as errf:
                    err_log = "\n".join(errf.readlines())
                msg = "Error bootstrapping controller: {}".format(err_log)
                app.log.error(msg)
                raise Exception('Unable to bootstrap (cloud type: {})'.format(
                    app.current_cloud_type))
                return

            self.emit('Bootstrap complete.')
            track_event("Juju Bootstrap", "Done", "")

            await juju.login()  # login to the newly created (default) model

            # Set provider type for post-bootstrap
            app.env['JUJU_PROVIDERTYPE'] = app.juju.client.info.provider_type
            app.env['JUJU_CONTROLLER'] = app.current_controller
            app.env['JUJU_MODEL'] = app.current_model

            await utils.run_step('00_post-bootstrap',
                                 'post-bootstrap',
                                 self.msg_cb,
                                 'Juju Post-Bootstrap')
        else:
            self.emit('Adding new model in the background.')
            track_event("Juju Add JaaS Model", "Started", "")
            await juju.add_model(app.current_model,
                                 app.current_controller,
                                 app.current_cloud)
            track_event("Juju Add JaaS Model", "Done", "")
            self.emit('Add model complete.')

    async def pre_bootstrap(self):
        """ runs pre bootstrap script if exists
        """

        # Set provider type for post-bootstrap
        app.env['JUJU_PROVIDERTYPE'] = juju.get_cloud_types_by_name()[
            app.current_cloud]
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model
        app.env['CONJURE_UP_SPELLSDIR'] = app.argv.spells_dir

        await utils.run_step('00_pre-bootstrap',
                             'pre-bootstrap',
                             self.msg_cb)

    def emit(self, msg):
        app.log.info(msg)
        self.msg_cb(msg)
