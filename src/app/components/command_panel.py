from typing import Callable
from tkinter import IntVar, Widget
from tkinter.ttk import Frame, Radiobutton, Button
from widgets import bind_tooltip

__all__ = ('CommandPanel', )

class CommandPanel(Frame):

    def __init__(self, parent: Widget | None = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.var = IntVar()
        self.frames: list[Frame] = []

    def _involve(self):
        frm = self.frames[self.var.get()]
        if frm.winfo_viewable():
            frm.place_forget()
        else:
            frm.place(x=self.winfo_x()+self.winfo_width()+5, y=self.winfo_y())

    def add(self, image: str | None = None, tooltip: str = "", *commands: tuple[str, str, Callable[..., None]]):
        """(image, tooltip, command)"""
        btn = Radiobutton(self, style='Toolbutton', image=image or "", variable=self.var, value=len(self.frames), command=self._involve)
        btn.grid(row=len(self.frames), column=0, sticky='nsew', padx=2, pady=2)
        if tooltip:
            bind_tooltip(btn, tooltip)
        frm = Frame(self.master)
        for (image, tooltip, command) in commands:
            btn = Button(frm, image=image, command=command)
            if tooltip:
                bind_tooltip(btn, tooltip)
            btn.grid(padx=5, pady=5)
        self.frames.append(frm)

    def disable(self):
        for w in self.children.values():
            w['state'] = 'disabled'
        for f in self.frames:
            for w in f.children.values():
                w['state'] = 'disabled'

    def enable(self):
        for w in self.children.values():
            w['state'] = 'normal'
        for f in self.frames:
            for w in f.children.values():
                w['state'] = 'normal'