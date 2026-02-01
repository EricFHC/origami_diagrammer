from tkinter.ttk import Frame, Label
from widgets import LoggingText
import logging

__all__ = ('LoggingPanel', )

class LoggingPanel(Frame):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.hand = Label(self, text="※")
        self.hand.pack(side='top', padx=(5, 2), pady=2)

        self.stream_handler = LoggingText(self, relief='flat')
        self.stream_handler.pack(fill='both', expand=True, padx=5, pady=5)
        self.stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S',
        ))
        self.stream_handler.setLevel('INFO')
