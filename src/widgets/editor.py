from tkinter import Widget, Event, StringVar, BooleanVar
from typing import Callable
from tkinter.ttk import Combobox, Entry, Checkbutton
from common import Cell, RefCell, Option, Callbacks

__all__ = ('Editor', 'ChoiceEditor', 'SwitchEditor')

class Editor:

    def create_widget(self, parent: Widget | None = None) -> Widget:
        raise NotImplementedError()

    def support_wait(self) -> bool:
        raise NotImplementedError()

    @property
    def on_change(self) -> Callbacks:
        raise NotImplementedError()

class ChoiceEditor[T](Editor):

    def __init__(self, value: Cell[T], /, from_value: Callable[[T], str], into_value: Callable[[str], Option[T]], choices: tuple[str, ...], *, with_default: bool = True, readonly: bool = False):
        super().__init__()
        self.value = value
        self.from_value = from_value
        self.into_value = into_value
        self.choices = choices
        self.with_default = with_default
        self.readonly = readonly

    @property
    def on_change(self) -> Callbacks[T]:
        return self.value.on_change

    def support_wait(self) -> bool:
        return (not self.with_default) and (not self.readonly)

    def create_widget(self, parent: Widget | None = None) -> Widget:
        cmb = Combobox(parent, state='disabled' if self.readonly else 'readonly', values=self.choices)

        # Bind ui change.
        if not self.readonly:
            def update(e: Event):
                v = self.into_value(e.widget.get())
                if v.is_none():
                    return
                self.value.set(v.unwrap())
            cmb.bind('<<ComboboxSelected>>', update)

        # Bind value change.
        set_: Callable[[T], None] = lambda x: cmb.set(self.from_value(x))
        self.value.on_change.bind(set_)
        cmb.bind('<Destroy>', lambda _: self.value.on_change.unbind(set_))

        if self.with_default:
            set_(self.value.get())

        return cmb

# class LineEditor[T](Editor):

#     def __init__(self, value: Cell[T], /, from_value: Callable[[T], str], into_value: Callable[[str], Option[T]], *, with_default: bool = True):
#         super().__init__()
#         self.value = value
#         self.from_value = from_value
#         self.into_value = into_value
#         self.with_default = with_default

#     @property
#     def on_change(self) -> Callbacks[T]:
#         return self.value.on_change

#     def support_wait(self) -> bool:
#         return not self.with_default

#     def create_widget(self, parent: Widget | None = None) -> Widget:
#         v = StringVar()
#         etr = Entry(parent, textvariable=v)

#         # Bind ui change.
#         def update(e: Event):
#             v = self.into_value(e.widget.get())
#             if v.is_none():
#                 return
#             self.value.set(v.unwrap())
#         etr.bind('<FocusOut>', update)

#         # Bind value change.
#         set_: Callable[[T], None] = lambda x: v.set(self.from_value(x))
#         self.value.on_change.bind(set_)
#         etr.bind('<Destroy>', lambda _: self.value.on_change.unbind(set_))

#         if self.with_default:
#             set_(self.value.get())

#         return etr

class SwitchEditor(Editor):

    def __init__(self, value: Cell[bool], /, *, readonly: bool = False):
        super().__init__()
        self.value = value
        self.readonly = readonly

    @property
    def on_change(self) -> Callbacks[bool]:
        return self.value.on_change

    def support_wait(self) -> bool:
        return False

    def create_widget(self, parent: Widget | None = None) -> Widget:
        v = BooleanVar()
        chk = Checkbutton(parent, style="switch.TCheckbutton", variable=v, onvalue=True, offvalue=False)
        if self.readonly:
            chk['state'] = 'disabled'

        # Bind ui change.
        if not self.readonly:
            chk['command'] = lambda: self.value.set(v.get())

        # Bind value change.
        set_: Callable[[bool], None] = lambda x: v.set(x)
        self.value.on_change.bind(set_)
        chk.bind('<Destroy>', lambda _: self.value.on_change.unbind(set_))

        return chk

# class ListEditor[T](Editor):

#     def __init__(self, value: RefCell[list[T], tuple[T]], /, from_element: Callable[[T], str], into_element: Callable[[str], Option[T]], *, with_default: bool = True, sep: str = ","):
#         self.value = value
#         self.from_element = from_element
#         self.into_element = into_element
#         self.with_default = with_default
#         self.sep = sep

#     @property
#     def on_change(self) -> Callbacks[tuple[T]]:
#         return self.value.on_change

#     def support_wait(self) -> bool:
#         return not self.with_default

#     def create_widget(self, parent: Widget | None = None) -> Widget:
#         v = StringVar()
#         etr = Entry(parent, textvariable=v)

#         # Bind ui change.
#         def update(e: Event):
#             a = []
#             for x in map(self.into_element, e.widget.get().split(self.sep)):
#                 if x.is_none():
#                     return
#                 a.append(x.unwrap())
#             with self.value.borrow_mut() as l:
#                 l.clear()
#                 l.extend(a)
#         etr.bind('<FocusOut>', update)

#         # Bind value change.
#         def set_(l: tuple[T]):
#             v.set(self.sep.join((map(self.from_element, l))))
#         self.value.on_change.bind(set_)
#         etr.bind('<Destroy>', lambda _: self.value.on_change.unbind(set_))

#         if self.with_default:
#             set_(self.value.borrow())

#         return etr
