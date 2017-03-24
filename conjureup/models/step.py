""" Step model
"""
import subprocess

from conjureup.app_config import app


class StepModel:

    def __init__(self, step, path):
        self.title = step.get('title', '')
        self.description = step.get('description', '')
        self.result = ''
        self.viewable = step.get('viewable', False)
        self.needs_sudo = step.get('sudo', False)
        self.additional_input = step.get('additional-input', [])
        self.path = path

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
        return "<t: {} d: {} v: {} p:>".format(self.title,
                                               self.description,
                                               self.viewable,
                                               self.path)

    def can_sudo(self, password=None):
        if password:
            password = '{}\n'.format(password).encode('utf8')
            result = subprocess.run(['sudo', '-S', '/bin/true'],
                                    input=password,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                return False
        result = subprocess.run(['sudo', '-n', '/bin/true'],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        return result.returncode == 0
