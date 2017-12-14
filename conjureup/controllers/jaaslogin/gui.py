import asyncio
from subprocess import CalledProcessError

from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.consts import JAAS_DOMAIN
from conjureup.ui.views.interstitial import InterstitialView
from conjureup.ui.views.jaas import JaaSLoginView


class JaaSLoginController:
    def __init__(self):
        self.authenticating = asyncio.Event()
        self.login_success = False
        self.login_error = None

    def render(self, going_back=False):
        if going_back:
            self.back()  # if going back, skip this screen entirely
            return

        if not app.jaas_controller:
            app.jaas_controller = 'jaas'

        if self.login_success:
            # already authed, don't waste time trying again
            self.finish()
        elif self.login_error is not None:
            # saved error, go straight to form
            self.render_login()
        else:
            # try to auth with cached creds
            self.render_interstitial()
            app.loop.create_task(self._try_token_auth())

    def render_interstitial(self):
        self.authenticating.set()
        view = InterstitialView(title="JaaS Login Wait",
                                message="Logging in to JaaS. Please wait.",
                                event=self.authenticating)
        view.show()

    def render_login(self):
        view = JaaSLoginView(self.register, self.back, self.login_error)
        view.show()

    async def _try_token_auth(self):
        app.log.info('Attempting to register JAAS with saved token')
        try:
            await juju.register_controller(app.jaas_controller,
                                           JAAS_DOMAIN,
                                           '', '', '')
            controllers.use('showsteps').render()
        except CalledProcessError:
            # empty-but-not-None message to skip retrying token auth
            self.login_error = ''
            self.render_login()

    def register(self, email=None, password=None, twofa=None):
        self.render_interstitial()
        app.loop.create_task(self._register(email, password, twofa))

    async def _register(self, email, password, twofa):
        if not await juju.register_controller(app.jaas_controller,
                                              JAAS_DOMAIN,
                                              email, password, twofa,
                                              fail_cb=self.fail,
                                              timeout_cb=self.timeout):
            return
        app.provider.controller = app.jaas_controller
        self.authenticating.clear()
        self.login_success = True
        self.login_error = None
        app.log.info('JAAS is registered')
        self.finish()

    def finish(self):
        app.is_jaas = True
        controllers.use('showsteps').render()

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
        self.login_error = msg
        self.render_login()

    def timeout(self):
        self.authenticating.clear()
        controllers = juju.get_controllers()
        if app.jaas_controller in controllers['controllers']:
            # registration seems to have worked; maybe we should remove and
            # try again to be safe, but hopefully it's safe to just move on
            return self.finish()
        self.login_error = 'Timed out connecting to JaaS.  Please try again.'
        self.render_login()

    def back(self):
        controllers.use('controllerpicker').render(going_back=True)


_controller_class = JaaSLoginController
