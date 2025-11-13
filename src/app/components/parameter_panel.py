from tkinter.ttk import *
from widgets import Editor

__all__ = ('ParameterPanel', )

class ParameterPanel(Frame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.n = 0
        self.f = Frame(self)
        self.f.pack(side='bottom', padx=5, pady=2)
        self.f.grid_columnconfigure(1, weight=1)

        Separator(self, orient='horizontal').pack(side='bottom', fill='x', padx=5, pady=5)

        self.lbl_name = Label(self, text="Unnamed Command")
        self.lbl_name.pack(side='left', padx=5, pady=2)

        self.btn_cancel = Button(self, text="✘", width=2, command=lambda: self.event_generate("<<Cancel>>"))
        self.btn_cancel.pack(side='right', padx=(2, 5), pady=2)

        self.btn_submit = Button(self, text="✔", width=2, command=lambda: self.event_generate("<<Submit>>"))
        self.btn_submit.pack(side='right', padx=2, pady=2)

    def set_name(self, name: str):
        self.lbl_name['text'] = name

    def add_editor(self, name: str, editor: Editor):
        Label(self.f, text=name).grid(row=self.n, column=0, padx=(5, 2), pady=2, sticky='nsew')
        editor.create_widget(self.f).grid(row=self.n, column=1, padx=(2, 5), pady=2, sticky='nsew')
        self.n += 1

    def clear_editor(self):
        for w in self.f.winfo_children():
            w.destroy()
        self.n = 0
