""" Step model
"""
import asyncio
import os
from pathlib import Path

import aiofiles
import yaml

from conjureup import juju
from conjureup.app_config import app
from conjureup.telemetry import track_event
from conjureup.utils import SudoError, can_sudo, is_linux, sentry_report


class StepModel:
    @classmethod
    def load_spell_steps(cls):
        steps_dir = Path(app.config['spell-dir']) / 'steps'
        app.steps = []
        for step_meta_path in sorted(steps_dir.glob('*')):
            step = StepModel.load(step_meta_path)
            app.steps.append(step)

    @classmethod
    def load(cls, step_meta_path):
        step_name = step_meta_path.stem
        step_ex_path = step_meta_path.parent / step_name
        if not (step_ex_path / 'metadata.yaml').is_file():
            raise ValidationError(
                'Step {} has no implementation'.format(step_name))
        # elif not os.access(str(step_ex_path), os.X_OK):
        #     raise ValidationError(
        #         'Step {} is not executable'.format(step_name))
        step_metadata = yaml.load(
            (step_meta_path / 'metadata.yaml').read_text())
        step = StepModel(step_metadata, step_name)
        step_data = app.steps_data.get(step.name, {})
        for field in step.additional_input:
            key = field['key']
            default = field.get('default')
            value = step_data.get(key, default)
            step_data[key] = value
        app.steps_data[step.name] = step_data
        return step

    def __init__(self, step, name):
        self.title = step.get('title', '')
        self.description = step.get('description', '')
        self.result = ''
        self.viewable = step.get('viewable', False)
        self.needs_sudo = step.get('sudo', False)
        self.additional_input = step.get('additional-input', [])
        self.cloud_whitelist = step.get('cloud-whitelist', [])
        self.name = name

    async def validate_input(self, msg_cb):
        """ validate-input phase
        """
        return await self.run('validate-input', msg_cb)

    async def after_input(self, msg_cb):
        """ after-input phase
        """
        return await self.run('after-input', msg_cb)

    async def before_deploy(self, msg_cb):
        """ before-deploy phase
        """
        return await self.run('before-deploy', msg_cb)

    async def after_deploy(self, msg_cb):
        """ after-deploy phase
        """
        return await self.run('after-deploy', msg_cb)

    def __getattr__(self, attr):
        """
        Override attribute lookup since ConsoleUI doesn't implement
        everything PegagusUI does.
        """

        def nofunc(*args, **kwargs):
            app.log.debug(attr)

        try:
            getattr(StepModel, attr)
        except:
            # Log the invalid attribute call
            setattr(self.__class__, attr, nofunc)
            return getattr(StepModel, attr)

    def __repr__(self):
        return "<t: {} d: {} v: {} c: {} f: {}>".format(self.title,
                                                        self.description,
                                                        self.viewable,
                                                        self.cloud_whitelist,
                                                        self.filename)

    async def run(self, phase, msg_cb, event_name=None):
        # Define STEP_NAME for use in determining where to store
        # our step results,
        #  state set "conjure-up.$SPELL_NAME.$STEP_NAME.result" "val"
        app.env['CONJURE_UP_STEP'] = self.name

        step_path = Path(app.config['spell-dir']) / 'steps' / self.name / phase

        if not step_path.is_file():
            return

        step_path = str(step_path)

        msg = "Running step: {}.".format(self.name)
        app.log.info(msg)
        msg_cb(msg)
        if event_name is not None:
            track_event(event_name, "Started", "")

        if not os.access(step_path, os.X_OK):
            raise Exception("Step {} not executable".format(self.title))

        if is_linux() and self.needs_sudo and not await can_sudo():
            raise SudoError('Step "{}" requires sudo: {}'.format(
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

        if provider_type == "maas":
            app.env['MAAS_ENDPOINT'] = app.maas.endpoint
            app.env['MAAS_APIKEY'] = app.maas.api_key

        for step_name, step_data in app.steps_data.items():
            for key, value in step_data.items():
                app.env[key.upper()] = step_data[key]

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

        async with aiofiles.open(step_path + ".out", 'w') as outf:
            async with aiofiles.open(step_path + ".err", 'w') as errf:
                proc = await asyncio.create_subprocess_exec(step_path,
                                                            env=app.env,
                                                            stdout=outf,
                                                            stderr=errf)
                async with aiofiles.open(step_path + '.out', 'r') as f:
                    while proc.returncode is None:
                        async for line in f:
                            msg_cb(line)
                        await asyncio.sleep(0.01)

        out_log = Path(step_path + '.out').read_text()
        err_log = Path(step_path + '.err').read_text()

        if proc.returncode != 0:
            app.sentry.context.merge({'extra': {
                'out_log_tail': out_log[-400:],
                'err_log_tail': err_log[-400:],
            }})
            raise Exception("Failure in step {}".format(self.filename))

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

        result_key = "conjure-up.{}.{}.result".format(app.config['spell'],
                                                      self.name)
        result = app.state.get(result_key)
        return (result or '')


class ValidationError(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(msg, *args, **kwargs)
