""" Step model
"""
from conjureup.app_config import app


class StepModel:
    def __init__(self, step, path):
        self.title = step.get('title', '')
        self.description = step.get('description', '')
        self.result = ''
        self.viewable = step.get('viewable', False)

        self.additional_input = step.get('additional-input', [])

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
