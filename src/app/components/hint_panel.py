from tkinter.ttk import Frame, Label

__all__ = ('HintPanel', )

class HintPanel(Frame):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.hand = Label(self, text="※")
        self.hand.pack(side='left', padx=(5, 2), pady=2)

        self._lbl = Label(self)
        self._lbl.pack(side='right', fill='x', padx=(2, 5), pady=2)

    def set(self, string: str | None):
        if string is None:
            self.lower()
        elif string:
            self._lbl['text'] = string
            self.tkraise()