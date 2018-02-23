""" Step model
"""
import os
from pathlib import Path

import aiofiles
import yaml

from conjureup import juju
from conjureup.app_config import app
from conjureup.consts import PHASES
from conjureup.telemetry import track_event
from conjureup.utils import SudoError, arun, can_sudo, is_linux, sentry_report


class StepModel:
    @classmethod
    def load_spell_steps(cls):
        spell_name = app.config['metadata']['friendly-name']
        steps_dir = Path(app.config['spell-dir']) / 'steps'
        app.steps = []
        for step_dir in sorted(steps_dir.glob('*')):
            if not step_dir.is_dir():
                continue
            step = StepModel.load(step_dir, source=spell_name)
            app.steps.append(step)
        app.log.debug('steps: {}'.format(app.steps))

    @classmethod
    def load(cls, step_meta_path, source):
        step_name = step_meta_path.stem
        step_ex_path = step_meta_path.parent / step_name
        if not (step_ex_path / 'metadata.yaml').is_file():
            raise ValidationError(
                'The {} step {} has no metadata'.format(source, step_name))
        step_metadata = yaml.load(
            (step_meta_path / 'metadata.yaml').read_text())
        step = StepModel(step_metadata, step_name, step_ex_path, source)
        if not any(step._has_phase(phase) for phase in PHASES):
            raise ValidationError(
                'The {} step {} has no implementation'.format(source,
                                                              step_name))
        step_data = app.steps_data.get(step.name, {})
        for field in step.additional_input:
            key = field['key']
            default = field.get('default')
            value = step_data.get(key, default)
            step_data[key] = value
        app.steps_data[step.name] = step_data
        # clear transient values
        step.set_state('bundle-add', None)
        step.set_state('bundle-remove', None)
        for phase in PHASES:
            step.set_state('result', None, phase)
        return step

    def __init__(self, step, name, step_path, source):
        self.title = step.get('title', '')
        self.description = step.get('description', '')
        self.result = ''
        self.viewable = step.get('viewable', False)
        self.required = step.get('required', False)
        self.needs_sudo = step.get('sudo', False)
        self.additional_input = step.get('additional-input', [])
        self.cloud_whitelist = step.get('cloud-whitelist', [])
        self.name = name
        self.step_path = step_path
        self.source = source

    def __repr__(self):
        return "<StepModel {} {} v: {} c: {}>".format(
            self.source, self.name, self.viewable, self.cloud_whitelist)

    def _build_phase_path(self, phase):
        return self.step_path / phase.value

    def _has_phase(self, phase):
        return self._build_phase_path(phase).is_file()

    @property
    def has_validate_input(self):
        return self._has_phase(PHASES.VALIDATE_INPUT)

    @property
    def has_after_input(self):
        return self._has_phase(PHASES.AFTER_INPUT)

    @property
    def has_before_deploy(self):
        return self._has_phase(PHASES.BEFORE_DEPLOY)

    @property
    def has_before_wait(self):
        return self._has_phase(PHASES.BEFORE_WAIT)

    @property
    def has_after_deploy(self):
        return self._has_phase(PHASES.AFTER_DEPLOY)

    async def validate_input(self, msg_cb):
        """ validate-input phase
        """
        return await self.run(PHASES.VALIDATE_INPUT, msg_cb)

    async def after_input(self, msg_cb):
        """ after-input phase
        """
        return await self.run(PHASES.AFTER_INPUT, msg_cb)

    async def before_deploy(self, msg_cb):
        """ before-deploy phase
        """
        return await self.run(PHASES.BEFORE_DEPLOY, msg_cb)

    async def before_wait(self, msg_cb):
        """ before-deploy phase
        """
        return await self.run(PHASES.BEFORE_WAIT, msg_cb)

    async def after_deploy(self, msg_cb):
        """ after-deploy phase
        """
        return await self.run(PHASES.AFTER_DEPLOY, msg_cb)

    def get_state(self, key, phase=None):
        """
        Return the state data value for the given key, namespaced by the
        spell, step, and optionally phase.
        """
        if phase is None:
            key = "conjure-up.{}.{}.{}".format(app.config['spell'],
                                               self.name,
                                               key)
        else:
            key = "conjure-up.{}.{}.{}.{}".format(app.config['spell'],
                                                  self.name,
                                                  phase.value,
                                                  key)
        return app.state.get(key) or ''

    def set_state(self, key, value, phase=None):
        """
        Set the state data value for the given key, namespaced by the
        spell, step, and optionally phase.
        """
        if phase is None:
            key = "conjure-up.{}.{}.{}".format(app.config['spell'],
                                               self.name,
                                               key)
        else:
            key = "conjure-up.{}.{}.{}.{}".format(app.config['spell'],
                                                  self.name,
                                                  phase.value,
                                                  key)
        app.state[key] = value

    @property
    def bundle_add(self):
        """
        Return the bundle-add fragment file, if set by this step.

        Return value is a Path object or None.
        """
        bundle_add = self.get_state('bundle-add')
        bundle_add_path = self.step_path / bundle_add
        if not bundle_add or not bundle_add_path.exists():
            return None
        return bundle_add_path

    @property
    def bundle_remove(self):
        """
        Return the bundle-remove fragment file, if set by this step.

        Return value is a Path object or None.
        """
        bundle_remove = self.get_state('bundle-remove')
        bundle_remove_path = self.step_path / bundle_remove
        if not bundle_remove or not bundle_remove_path.exists():
            return None
        return bundle_remove_path

    async def run(self, phase, msg_cb, event_name=None):
        # Define STEP_NAME for use in determining where to store
        # our step results,
        #  state set "conjure-up.$SPELL_NAME.$STEP_NAME.result" "val"
        app.env['CONJURE_UP_STEP'] = self.name
        app.env['CONJURE_UP_PHASE'] = phase.value

        step_path = self._build_phase_path(phase)

        if not step_path.is_file():
            return

        if not os.access(str(step_path), os.X_OK):
            app.log.error(
                'Unable to run {} step {} {}, it is not executable'.format(
                    self.source, step_path.stem, phase.value))
            return

        step_path = str(step_path)

        msg = "Running {} step: {} {}.".format(self.source,
                                               self.name,
                                               phase.value)
        app.log.info(msg)
        msg_cb(msg)
        if event_name is not None:
            track_event(event_name, "Started", "")

        if is_linux() and self.needs_sudo and not await can_sudo():
            raise SudoError('The "{}" step "{}" requires sudo: {}'.format(
                self.source,
                self.title,
                'password failed' if app.sudo_pass else
                'passwordless sudo required',
            ))

        cloud_types = juju.get_cloud_types_by_name()
        provider_type = cloud_types[app.provider.cloud]

        app.env['JUJU_PROVIDERTYPE'] = provider_type
        # not all providers have a credential, e.g., localhost
        app.env['JUJU_CREDENTIAL'] = app.provider.credential or ''
        app.env['JUJU_CONTROLLER'] = app.provider.controller
        app.env['JUJU_MODEL'] = app.provider.model
        app.env['JUJU_REGION'] = app.provider.region or ''
        app.env['CONJURE_UP_SPELLSDIR'] = app.argv.spells_dir
        app.env['CONJURE_UP_SESSION_ID'] = app.session_id

        if provider_type == "maas":
            app.env['MAAS_ENDPOINT'] = app.maas.endpoint
            app.env['MAAS_APIKEY'] = app.maas.api_key

        for step_name, step_data in app.steps_data.items():
            for key, value in step_data.items():
                app.env[key.upper()] = str(step_data[key])

        for key, value in app.env.items():
            if value is None:
                app.log.warning('Env {} is None; '
                                'replacing with empty string'.format(key))
                app.env[key] = ''

        app.log.debug("Storing environment")
        async with aiofiles.open(step_path + ".env", 'w') as outf:
            for k, v in app.env.items():
                if 'JUJU' in k or 'MAAS' in k or 'CONJURE' in k:
                    await outf.write("{}=\"{}\" ".format(k.upper(), v))

        app.log.debug("Executing script: {}".format(step_path))

        out_path = step_path + '.out'
        err_path = step_path + '.err'
        ret, out_log, err_log = await arun([step_path],
                                           stdout=out_path,
                                           stderr=err_path,
                                           cb_stdout=msg_cb)

        if ret != 0:
            app.sentry.context.merge({'extra': {
                'out_log_tail': out_log[-400:],
                'err_log_tail': err_log[-400:],
            }})
            raise Exception("Failure in step {} {}".format(self.name,
                                                           phase.value))

        # special case for 00_deploy-done to report masked
        # charm hook failures that were retried automatically
        if not app.noreport:
            failed_apps = set()  # only report each charm once
            for line in err_log.splitlines():
                if 'hook failure, will retry' in line:
                    log_leader = line.split()[0]
                    unit_name = log_leader.split(':')[-1]
                    app_name = unit_name.split('/')[0]
                    failed_apps.add(app_name)
            for app_name in failed_apps:
                # report each individually so that Sentry will give us a
                # breakdown of failures per-charm in addition to per-spell
                sentry_report('Retried hook failure', tags={
                    'app_name': app_name,
                })

        if event_name is not None:
            track_event(event_name, "Done", "")

        return self.get_state('result', phase)


class ValidationError(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(msg, *args, **kwargs)
