from pathlib import Path

from conjureup import controllers, events, juju, utils
from conjureup.app_config import app
from conjureup.models.step import StepModel
from conjureup.telemetry import track_event


class BaseBootstrapController:
    msg_cb = NotImplementedError()

    def render(self):
        app.loop.create_task(self.do_bootstrap(app.current_credential))
        controllers.use('bootstrapwait').render()

    async def do_bootstrap(self, creds):
        if app.is_jaas:
            return

        await self.pre_bootstrap()
        self.emit('Bootstrapping Juju controller.')
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
            log_file = '{}-bootstrap.err'.format(app.current_controller)
            log_file = Path(app.config['spell-dir']) / log_file
            err_log = log_file.read_text('utf8').splitlines()
            app.log.error("Error bootstrapping controller: "
                          "{}".format(err_log))
            app.sentry.context.merge({'extra': {'err_log': err_log[-400:]}})
            raise Exception('Unable to bootstrap (cloud type: {})'.format(
                app.current_cloud_type))

        self.emit('Bootstrap complete.')
        track_event("Juju Bootstrap", "Done", "")

        await juju.login()  # login to the newly created (default) model

        # Set provider type for post-bootstrap
        app.env['JUJU_PROVIDERTYPE'] = app.juju.client.info.provider_type
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model

        step = StepModel({},
                         filename='00_post-bootstrap',
                         name='post-bootstrap')
        await utils.run_step(step,
                             self.msg_cb,
                             'Juju Post-Bootstrap')
        events.Bootstrapped.set()

    async def pre_bootstrap(self):
        """ runs pre bootstrap script if exists
        """

        # Set provider type for post-bootstrap
        app.env['JUJU_PROVIDERTYPE'] = juju.get_cloud_types_by_name()[
            app.current_cloud]
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model
        app.env['CONJURE_UP_SPELLSDIR'] = app.argv.spells_dir

        step = StepModel({},
                         filename='00_pre-bootstrap',
                         name='pre-bootstrap')
        await utils.run_step(step,
                             self.msg_cb)

    def emit(self, msg):
        app.log.info(msg)
        self.msg_cb(msg)
