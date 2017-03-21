from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.consts import JAAS_DOMAIN
from conjureup.telemetry import track_exception, track_screen
from conjureup.ui.views.bootstrapwait import BootstrapWaitView
from conjureup.ui.views.jaas import JaaSLoginView
from ubuntui.ev import EventLoop


class JaaSLoginController:

    def __init__(self):
        self.alarm_handle = None
        self.view = None

    def __handle_exception(self, exc):
        track_exception(exc.args[0])
        return app.ui.show_exception_message(exc)

    def render(self):
        if app.jaas_controller:
            self.render_interstitial()
            self.finish()
        else:
            self.render_form(error=None)

    def render_form(self, error):
        if juju.has_jaas_auth() and not error:
            self.register()
            return
        track_screen("Login to JaaS")
        app.ui.set_header(
            title="Login to JaaS",
            excerpt='Enter your Ubuntu SSO credentials'
        )
        app.ui.set_body(JaaSLoginView(app,
                                      error=error,
                                      cb=self.register))

    def register(self, email=None, password=None, twofa=None):
        if not app.jaas_controller:
            app.jaas_controller = 'jaas'
        juju.register_controller(app.jaas_controller, JAAS_DOMAIN,
                                 email, password, twofa,
                                 cb=self.finish,
                                 fail_cb=self.fail,
                                 timeout_cb=self.timeout,
                                 exc_cb=self.__handle_exception)
        self.render_interstitial()

    def __refresh(self, *args):
        if self.view:
            self.view.redraw_kitt()
            self.alarm_handle = EventLoop.set_alarm_in(
                1, self.__refresh)

    def __remove_alarm(self):
        if self.alarm_handle:
            EventLoop.remove_alarm(self.alarm_handle)

    def render_interstitial(self):
        track_screen("JaaS Login Wait")
        app.ui.set_header(title="Waiting")
        self.view = BootstrapWaitView(
            app=app,
            message="Logging in to JaaS. Please wait.")
        app.ui.set_body(self.view)
        self.__refresh()

    def fail(self, stderr):
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
        self.__remove_alarm()
        self.render_form(error=msg)

    def timeout(self):
        controllers = juju.get_controllers()
        if app.jaas_controller in controllers['controllers']:
            # registration seems to have worked; maybe we should remove and
            # try again to be safe, but hopefully it's safe to just move on
            return self.finish()
        self.__remove_alarm()
        self.render_form(error='Timed out connecting to JaaS.  '
                               'Please try again.')

    def finish(self):
        app.current_controller = app.jaas_controller
        app.is_jaas = True
        self.__remove_alarm()
        controllers.use('clouds').render()


_controller_class = JaaSLoginController
