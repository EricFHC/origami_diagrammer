from tkinter import Text
import logging

class LoggingText(Text, logging.Handler):

    def __init__(self, parent=None, **kwargs):
        Text.__init__(self, parent, **kwargs)
        logging.Handler.__init__(self)

    def set_default_style(self):
        self.tag_config('INFO', foreground='black')
        self.tag_config('WARNING', foreground='orange')
        self.tag_config('ERROR', foreground='red')

    def emit(self, record):
        try:
            msg = self.format(record)
            level = record.levelname
            self.insert('end', msg + '\n', level)
            self.see('end')
        except Exception:
            self.handleError(record)