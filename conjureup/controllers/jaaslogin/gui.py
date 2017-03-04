import asyncio

from conjureup import controllers, events, juju
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
        app.jaas_controller = 'jaas'
        await juju.register_controller(app.jaas_controller,
                                       JAAS_DOMAIN,
                                       email, password, twofa,
                                       fail_cb=self.fail,
                                       timeout_cb=self.timeout)
        app.current_controller = app.jaas_controller
        app.is_jaas = True
        self.authenticating.clear()
        events.Bootstrapped.set()
        controllers.use('clouds').render()

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
        prefix = 'ERROR cannot get token: '
        if msg.startswith(prefix):
            msg = 'Login failed, please try again: {}'.format(
                msg[len(prefix):])
        prefix = 'Invalid request data (email: ['
        if msg.startswith(prefix):
            msg = 'Login failed, please try again: {}'.format(
                msg[len(prefix):][:-3])  # also strip trailing ])
        prefix = 'ERROR cannot get user details for'
        if msg.startswith(prefix):
            msg = ('USSO account not connected with JaaS.  Please login via '
                   'your browser at https://jujucharms.com/login to connect '
                   'your account, and then try this login again.')
        self.render_form(error=msg)

    def timeout(self):
        self.authenticating.clear()
        controllers = juju.get_controllers()
        if app.jaas_controller in controllers['controllers']:
            # registration seems to have worked; maybe we should remove and
            # try again to be safe, but hopefully it's safe to just move on
            return self.finish()
        self.__remove_alarm()
        self.render_form(error='Timed out connecting to JaaS.  '
                               'Please try again.')


_controller_class = JaaSLoginController
