from urwid import Text


class Instruction(Text):

    def __init__(self, text, **kwargs):
        super().__init__(('info_context', text), **kwargs)


class ColumnHeader(Text):

    def __init__(self, text, **kwargs):
        super().__init__(('info_context', text), **kwargs)
