from pathlib import Path

from conjureup import errors, events, juju
from conjureup.app_config import app
from conjureup.telemetry import track_event


class BaseBootstrapController:
    msg_cb = NotImplementedError()

    def is_existing_controller(self):
        controllers = juju.get_controllers()['controllers']
        return app.provider.controller in controllers

    async def run(self):
        await app.provider.configure_tools()

        if app.is_jaas or self.is_existing_controller():
            await self.do_add_model()
        else:
            await self.do_bootstrap()

    async def do_add_model(self):
        if await juju.model_available():
            self.emit('Connecting to Juju model {}...'.format(
                app.provider.model))
            await juju.connect_model()
            self.emit('Juju model connected.')
        else:
            self.emit('Creating Juju model {}...'.format(
                app.provider.model))
            cloud_with_region = app.provider.cloud
            if app.provider.region:
                cloud_with_region = '/'.join([app.provider.cloud,
                                              app.provider.region])
            track_event("Juju Add Model", "Started", "{}{}".format(
                cloud_with_region, ' on JAAS' if app.is_jaas else ''))
            await juju.create_model()
            track_event("Juju Add Model", "Done", "{}{}".format(
                cloud_with_region, 'on JAAS' if app.is_jaas else ''))
            self.emit('Juju model created.')
        events.Bootstrapped.set()

    async def do_bootstrap(self):
        self.emit('Bootstrapping Juju controller...')
        track_event("Juju Bootstrap", "Started", "")
        cloud_with_region = app.provider.cloud
        if app.provider.region:
            cloud_with_region = '/'.join([app.provider.cloud,
                                          app.provider.region])
        success = await juju.bootstrap(app.provider.controller,
                                       cloud_with_region,
                                       app.provider.model,
                                       credential=app.provider.credential)
        if not success:
            log_file = '{}-bootstrap.err'.format(app.provider.controller)
            log_file = Path(app.config['spell-dir']) / log_file
            err_log = log_file.read_text('utf8').splitlines()
            app.log.error("Error bootstrapping controller: "
                          "{}".format(err_log))
            err_tail = err_log[-400:]
            app.sentry.context.merge({'extra': {'err_tail': err_tail}})
            raise errors.BootstrapError(
                'Unable to bootstrap (cloud type: {})'.format(
                    app.provider.cloud_type))

        self.emit('Bootstrap complete.')
        track_event("Juju Bootstrap", "Done", "")

        await juju.connect_model()  # login to newly created (default) model
        events.Bootstrapped.set()

    def emit(self, msg):
        app.log.info(msg)
        self.msg_cb(msg)
