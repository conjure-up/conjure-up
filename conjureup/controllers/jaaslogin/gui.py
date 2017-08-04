import asyncio
from subprocess import CalledProcessError

from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.consts import JAAS_DOMAIN
from conjureup.telemetry import track_screen
from conjureup.ui.views.bootstrapwait import BootstrapWaitView
from conjureup.ui.views.jaas import JaaSLoginView


class JaaSLoginController:
    def __init__(self):
        self.authenticating = asyncio.Event()
        self.view = None

    def render(self, error=None):
        app.jaas_controller = 'jaas'
        self.render_interstitial()
        app.loop.create_task(self._try_token_auth(error))

    async def _try_token_auth(self, error):
        app.log.info('Attempting to register JAAS with saved token')
        try:
            await juju.register_controller(app.jaas_controller,
                                           JAAS_DOMAIN,
                                           '', '', '')
            controllers.use('showsteps').render()
        except CalledProcessError:
            self.show_login_screen(error)

    def show_login_screen(self, error):
        track_screen("Login to JaaS")
        app.ui.set_header(
            title="Login to JaaS",
            excerpt='Enter your Ubuntu SSO credentials'
        )
        app.ui.set_body(JaaSLoginView(app,
                                      error=error,
                                      cb=self.register))

    def register(self, email=None, password=None, twofa=None):
        app.loop.create_task(self._register(email, password, twofa))
        self.render_interstitial()

    async def _register(self, email, password, twofa):
        if not await juju.register_controller(app.jaas_controller,
                                              JAAS_DOMAIN,
                                              email, password, twofa,
                                              fail_cb=self.fail,
                                              timeout_cb=self.timeout):
            return
        app.provider.controller = app.jaas_controller
        app.is_jaas = True
        self.authenticating.clear()
        app.log.info('JAAS is registered')
        controllers.use('showsteps').render()

    def render_interstitial(self):
        track_screen("JaaS Login Wait")
        app.ui.set_header(title="Waiting")
        self.view = BootstrapWaitView(
            app=app,
            message="Logging in to JaaS. Please wait.")
        app.ui.set_body(self.view)
        self.authenticating.set()
        app.loop.create_task(self._refresh())
        self._refresh()

    async def _refresh(self):
        while self.authenticating.is_set():
            self.view.redraw_kitt()
            await asyncio.sleep(1)

    def fail(self, stderr):
        self.authenticating.clear()
        msg = stderr
        if 'ERROR cannot get user details for' in msg:
            msg = ('USSO account not connected with JaaS.  Please login via '
                   'your browser at https://jujucharms.com/login to connect '
                   'your account, and then try this login again.')
        else:
            prefix = 'ERROR cannot get token: '
            if msg.startswith(prefix):
                msg = msg[len(prefix):]
            prefix = 'Invalid request data (email: ['
            if msg.startswith(prefix):
                msg = msg[len(prefix):][:-3]  # also strip trailing ])
            msg = 'Login failed, please try again: {}'.format(msg)
        self.render(error=msg)

    def timeout(self):
        self.authenticating.clear()
        controllers = juju.get_controllers()
        if app.jaas_controller in controllers['controllers']:
            # registration seems to have worked; maybe we should remove and
            # try again to be safe, but hopefully it's safe to just move on
            return self.finish()
        self.__remove_alarm()
        self.render(error='Timed out connecting to JaaS.  Please try again.')


_controller_class = JaaSLoginController
