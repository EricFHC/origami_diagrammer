from typing import Literal
from tkinter.ttk import Label

__all__ = ('HintPanel', )

class HintPanel(Label):

    COLORS = {
        'info': 'black',
        'error': 'red',
    }

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    def push_message(self, message: str, level: Literal['info', 'error'] = 'info'):
        self['text'] = message
        self['foreground'] = self.COLORS.get(level, 'black')