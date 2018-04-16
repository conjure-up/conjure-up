""" application config
"""
import json
from types import SimpleNamespace

bootstrap = SimpleNamespace(
    # Is bootstrap running
    running=False,

    # Attached output
    output=None
)

maas = SimpleNamespace(
    # Client
    client=None,

    # API key
    api_key=None,

    # API Endpoint
    endpoint=None
)

juju = SimpleNamespace(
    # Client
    client=None,

    # Is authenticated?
    authenticated=False,

    # Path to juju binary
    bin_path=None,

    # Path to juju-wait binary
    wait_path=None,

    # Charmstore
    charmstore=None
)


class AppConfig:
    """ Application config storage
    """
    # MAAS client
    # TODO: move this into MAAS provider
    maas = maas

    # Juju bootstrap details
    bootstrap = bootstrap

    # Juju Provider
    provider = None

    # Juju Client
    juju = juju

    # The conjure-up UI framework
    ui = None

    # Contains spell name
    config = None

    # Conjurefile
    conjurefile = None

    # Spell metadata
    metadata = None

    # List of multiple bundles, usually from a charmstore search
    bundles = None

    # Selected bundle from a Variant view
    current_bundle = None

    # Is JAAS supported by the current spell
    jaas_ok = True

    # Which controller, if any, is the JAAS controller
    jaas_controller = None

    # Whether the JAAS controller is selected
    is_jaas = False

    # Current UI View rendered
    current_view = None

    # Session ID for current deployment
    session_id = None

    # Application logger
    log = None

    # Charm store metadata API client
    metadata_controller = None

    # disable telemetry tracking
    no_track = False

    # disable automatic error reporting
    no_report = False

    # Application environment passed to processing steps
    env = None

    # Did deployment complete
    complete = False

    # Run in non interactive mode
    headless = False

    # Remote endpoint type (An enum, see download.py)
    endpoint_type = None

    # Reference to asyncio loop so that it can be accessed from other threads
    loop = None

    # State storage
    state = None

    # Sentry endpoint
    sentry = None

    # Spells index
    spells_index = None

    # Password for sudo, if needed
    sudo_pass = None

    # Step descriptions
    steps = None

    # Step user data
    steps_data = {}

    # exit code for conjure-up to terminate with
    exit_code = 0

    # All available addons by name
    addons = {}

    # Addon aliases for required spells
    addons_aliases = {}

    # Selected addons
    selected_addons = []

    spell_given = False

    alias_given = False

    def __setattr__(self, name, value):
        """ Gaurds against setting attributes that don't already exist
        """
        try:
            getattr(AppConfig, name)
        except AttributeError:
            raise Exception(
                "Attempted to set an unknown attribute for application config")
        super().__setattr__(name, value)

    @property
    def _internal_state_key(self):
        """ Internal, formatted namespace key
        """
        return "conjure-up.{}.{}".format(self.provider.cloud_type,
                                         self.config['spell'])

    @property
    def all_steps(self):
        """
        All steps, including those from selected addons.
        """
        from conjureup.models.addon import AddonModel
        return app.steps + AddonModel.selected_addons_steps()

    @property
    def has_bundle_modifications(self):
        """
        Whether or not any step modifies the bundle.
        """
        return any(step.bundle_add or step.bundle_remove
                   for step in self.all_steps)

    def to_json(self):
        """
        Serialize application config to JSON

        We blacklist several items as they are intended to be reloaded during
        every invocation of conjure-up. Also blacklist env for security
        precautions.
        """
        blacklist = ['loop', 'log', 'maas', 'argv', 'spells_index',
                     'juju', 'ui', 'bootstrap', 'endpoint_type', 'provider',
                     'metadata_controller', 'state',
                     'env', 'sentry', 'steps', 'sudo_pass', 'addons']
        new_dict = {}
        for k, v in self.__dict__.items():
            if k.startswith('__') or callable(getattr(self, k)):
                continue
            if k in blacklist:
                continue
            new_dict[k] = v
        return json.dumps(new_dict)

    def from_json(self, data):
        """ Deserializes application state and updates app_config
        """
        if isinstance(data, bytes):
            data = data.decode('utf8')
        state = json.loads(data)
        for k, v in state.items():
            try:
                getattr(self, k)
            except AttributeError:
                continue
            setattr(self, k, v)

    async def save(self):
        if not self.provider:
            # don't bother saving if they haven't even picked a cloud yet
            return
        self.log.info('Storing conjure-up state')
        if self.juju.authenticated:
            await self.juju.client.set_config(
                {'extra-info': self.to_json()})
            self.log.info('State saved in model config')
            # Check for existing key and clear it
            self.state.pop(self._internal_state_key, None)
        else:
            self.state[self._internal_state_key] = self.to_json()
            self.log.info('State saved')

    async def restore(self):
        self.log.info('Attempting to load conjure-up cached state.')
        try:
            if self.juju.authenticated:
                result = await self.juju.client.get_config()
                if 'extra-info' in result:
                    self.log.info(
                        "Found cached state from Juju model, reloading.")
                    self.from_json(result['extra-info'].value)
                    return
            result = self.state.get(self._internal_state_key)
            if result:
                self.log.info("Found cached state, reloading.")
                self.from_json(result)
        except json.JSONDecodeError as e:
            # Dont fail fatally if state information is incorrect. Just log it
            # and move on
            self.log.debug(
                "State information possibly corrupt "
                "or malformed: {}".format(e))


app = AppConfig()
