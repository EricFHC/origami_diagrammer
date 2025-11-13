from typing import Callable, Literal, ItemsView
from tkinter import Toplevel, Event
from tkinter.ttk import Frame, Label, Button

type KeySeq = tuple[str, ...]

class KeyName:

    CONTROL = "Control"
    ALT = "Alt"
    SHIFT = "Shift"

class AccGroupTable(Frame):

    def __init__(self, parent=None, callback: None | Callable[[str, KeySeq], None] = None):
        super().__init__(parent)
        self._accelerators: dict[str, KeySeq] = {}
        self._lines: dict[str, Button] = {}
        self._callback = callback

    def add(self, name: str, key_seq: KeySeq, type_: Literal['normal', 'hidden', 'readonly'] = 'normal'):
        self._accelerators[name] = key_seq
        if type_ == 'hidden':
            return
        r = len(self._accelerators)
        Label(self, text=name).grid(row=r, column=0, padx=5, pady=5)
        b = Button(self, text="+".join(key_seq))
        b.grid(row=r, column=1, sticky='w', padx=5, pady=5)
        self._lines[name] = b
        if type_ == 'readonly':
            b['state'] = 'disabled'
        else:
            b['command'] = lambda: self.edit(name)

    def edit(self, name: str):
        def callback(ks: KeySeq):
            self._lines[name]['text'] = "+".join(ks)
            if self._callback:
                self._callback(name, ks)
        popup = AccGroupPopup(self, self._accelerators, name, callback)
        popup.resizable(False, False)

        popup.deiconify()
        popup.focus_force()
        popup.grab_set()
        self.wait_window(popup)

class AccGroupPopup(Toplevel):

    def __init__(self, parent, group: dict[str, KeySeq], target: str, callback: Callable[[KeySeq], None] | None = None):
        super().__init__(parent)

        self._group = group
        self._target = target
        self._callback = callback

        self.title("Modify accelerator")

        self._setup_ui()
        self.bind('<Key>', self._on_key_press)

    def _setup_ui(self):
        Label(
            self,
            text="Press any key to modify the accelerator, except that:\n*pressing `Backspace` to undo,"\
            "\n*pressing `Enter` to submit, and\n*pressing `Esc` to cancel.",
            wraplength=400
        ).pack(side='top', fill='x', anchor='w', padx=5, pady=5)

        self._frm_sequence = Frame(self)
        self._frm_sequence.pack(side='top', fill='x', padx=5, pady=5)
        self._sequence: list[Button] = []

        self.lbl_possible_conflicts = Label(self)
        self.lbl_possible_conflicts.pack(side='top', anchor='w', padx=5, pady=5)
        self._update_possible_conflict()

        self.btn_submit = Button(self, text="✔", takefocus=False, command=self.submit)
        self.btn_submit.pack(side='right', padx=5, pady=5)

        self.btn_cancel = Button(self, text="✘", takefocus=False, command=self.cancel)
        self.btn_cancel.pack(side='right', padx=5, pady=5)

    def get_sequence(self) -> KeySeq:
        return tuple(map(lambda b: b.cget('text'), self._sequence))
    
    def _update_possible_conflict(self):
        s = self.get_sequence()

        def may_conflict(target: KeySeq) -> bool:
            return len(s) <= len(target) and all(s1 == s2 for s1, s2 in zip(s, target))
        possible_conflicts = {n: ks for n, ks in self._group.items() if n != self._target and may_conflict(ks)} if s else self._group

        if possible_conflicts:
            self.lbl_possible_conflicts['text'] = "Existing accelerators:\n" + "\n".join(f"{n}: {"+".join(ks)}" for n, ks in possible_conflicts.items())
        else:
            self.lbl_possible_conflicts['text'] = "No existing accelerators."

    def _on_key_press(self, e: Event):
        # Enter.
        if e.keysym_num == 65293: self.submit()
        # Esc.
        elif e.keysym_num == 65307: self.cancel()
        # Backspace.
        elif e.keysym_num == 65288 and self._sequence:
            self._sequence.pop().destroy()
            self._update_possible_conflict()
        else:
            m = {
                65505: KeyName.SHIFT, 65506: KeyName.SHIFT,
                65507: KeyName.CONTROL, 65508: KeyName.CONTROL,
                65513: KeyName.ALT, 65514: KeyName.ALT,
                **{i+65:w for i, w in enumerate('abcdefghijklmnopqrstuvwxyz')},
                **{i+97:w for i, w in enumerate('abcdefghijklmnopqrstuvwxyz')}
            }
            if not (w:=m.get(e.keysym_num)): return
            b = Button(self._frm_sequence, text=w, state='disabled')
            b.pack(side='left', padx=3, pady=2)
            self._sequence.append(b)
            self._update_possible_conflict()

    def submit(self):
        s = self.get_sequence()
        if (not s) or any(s==o for o in self._group.values()):
            self.destroy()
            return
        if self._callback is not None:
            self._callback(s)
        self.destroy()

    def cancel(self):
        self.destroy()

if __name__ == '__main__':
    from tkinter import Tk, Text

    root = Tk()
    root.title("Accelerator Editor Test")

    text = Text(root, relief='flat', width=50)
    text.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

    def callback(name: str, ks: KeySeq):
        text.insert('end', f"Set `{name}` to `{"+".join(ks)}`.\n")

    table = AccGroupTable(root, callback)
    table.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

    table.add("Save", (KeyName.CONTROL, 's'))
    table.add("Save as", (KeyName.SHIFT, KeyName.ALT, 's'))
    table.add("Open", (KeyName.CONTROL, 'o'))
    table.add("New file", (KeyName.CONTROL, 'n'), 'readonly')
    table.add("Copy", (KeyName.CONTROL, 'c'), 'hidden')
    table.add("Paste", (KeyName.CONTROL, 'v'), 'hidden')

    root.mainloop()
