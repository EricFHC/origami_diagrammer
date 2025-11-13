# TODO: Waiting for value checks in a lot of methods!!❤❤

from typing import Any, Literal
from dataclasses import dataclass
from tkinter import Canvas, Event, IntVar
import sys
sys.path.append(r'D:\projects\origami_diagram\src')
from common import IteratorWrap

__all__ = ('ItemState', 'StyleManager', 'CanvasPlus')

ItemState = Literal['normal', 'hover', 'selected', 'selected-hover']

class StyleManager:

    def __init__(self):
        self.styles: dict[str, dict] = {
            "TLine": {},
            "TPoly": {},
            "TOval": {}
        }

    # TODO: add checks
    def configure(self, name: str, **kwargs: tuple[Any, Any, Any, Any]):
        self.styles[name] = {
            s: {k: kwargs[k][i] for k in kwargs}
            for i, s in enumerate(('normal', 'hover', 'selected', 'selected-hover'))
        }

    def get(self, name: str, state: ItemState) -> dict:
        d = {}
        a = name.split('.')
        for sub_name in IteratorWrap(range(len(a))).map(lambda i: '.'.join(a[-i-1:])):
            d |= self.styles[sub_name][state]
        return d

    @staticmethod
    def is_sub_style(sub_style: str, style: str) -> bool:
        return style.endswith(sub_style)

@dataclass
class ItemData[U]:

    userdata: U
    style: str

class CanvasPlus[U](Canvas):

    def __init__(self, master=None, style: StyleManager | None = None, **kwargs):
        super().__init__(master, **kwargs)

        self.style = style or StyleManager()

        self.mapper: dict[U, int] = {}
        self.mapper_inverse: dict[int, ItemData[U]] = {}

        self.permit_user_deselect = False
        self.selection: set[int] = set()
        self._selection_change: int = -1
        self.selection_change: U
        self._init_selection()

    # ------------------------------Draw------------------------------

    def _add_item(self, create_func, *coords: tuple[int, int], userdata: U, style: str):
        item_id = create_func(*IteratorWrap(coords).flatten(), **self.style.get(style, 'normal'))
        self.mapper[userdata] = item_id
        self.mapper_inverse[item_id] = ItemData(userdata, style)

    def add_line(self, p1: tuple[int, int], p2: tuple[int, int], userdata: U, style: str = "TLine"):
        self._add_item(self.create_line, p1, p2, userdata=userdata, style=style)

    def add_poly(self, *p: tuple[int, int], userdata: U, style: str = "TPoly"):
        self._add_item(self.create_polygon, *p, userdata=userdata, style=style)

    # ------------------------------Selecting------------------------------

    def _init_selection(self):
        hover_id = -1

        def on_enter(_):
            nonlocal hover_id
            hover_id = self.find_withtag('current')[0]
            if hover_id in self.selection:
                self.itemconfigure(hover_id, self.style.get(self.mapper_inverse[hover_id].style, 'selected-hover'))
            else:
                self.itemconfigure(hover_id, self.style.get(self.mapper_inverse[hover_id].style, 'hover'))

        def on_press(_):
            nonlocal hover_id
            # SAFETY
            # Due to the trigger order of events, `hover_id` must point to the item under the mouse.
            self._selection_change = hover_id
            self.selection_change = self.mapper_inverse[hover_id].userdata
            if hover_id in self.selection:
                if self.permit_user_deselect:
                    self.selection.remove(hover_id)
                    self.itemconfigure(hover_id, self.style.get(self.mapper_inverse[hover_id].style, 'hover'))
                    self.event_generate('<<Deselect>>', data=hover_id)
            else:
                self.selection.add(hover_id)
                self.itemconfigure(hover_id, self.style.get(self.mapper_inverse[hover_id].style, 'selected-hover'))
                self.event_generate('<<Select>>', data=hover_id)

        def on_leave(_):
            nonlocal hover_id
            # SAFETY
            # The same as `on_press`.(～￣▽￣)～
            if hover_id in self.selection:
                self.itemconfigure(hover_id, self.style.get(self.mapper_inverse[hover_id].style, 'selected'))
            else:
                self.itemconfigure(hover_id, self.style.get(self.mapper_inverse[hover_id].style, 'normal'))
            hover_id = -1

        self.tag_bind('selectable', '<Enter>', on_enter)
        self.tag_bind('selectable', '<Leave>', on_leave)
        self.tag_bind('selectable', '<ButtonRelease-1>', on_press)

    def enable_selection_of_style(self, style: str):
        for i, d in self.mapper_inverse.items():
            if StyleManager.is_sub_style(d.style, style):
                self.addtag_withtag('selectable', i)

    def disable_selection_of_style(self, style: str):
        for i, d in self.mapper_inverse.items():
            if StyleManager.is_sub_style(d.style, style):
                self.dtag(i, 'selectable')

    def enable_selection_all(self):
        self.addtag_withtag('selectable', 'all')

    def disable_selection_all(self):
        self.dtag('all', 'selectable')

    def enable_selection(self, *userdata: U):
        for i in map(self.mapper.__getitem__, userdata):
            self.addtag_withtag('selectable', i)

    def disable_selection(self, *userdata: U):
        for i in map(self.mapper.__getitem__, userdata):
            self.dtag(i, 'selectable')

    def select(self, item: U):
        i = self.mapper[item]
        if i in self.selection:
            return
        self.selection.add(i)
        self.itemconfigure(i, self.style.get(self.mapper_inverse[i].style, 'selected'))

    def deselect(self, item: U):
        i = self.mapper[item]
        if i not in self.selection:
            return
        self.selection.remove(i)
        self.itemconfigure(i, self.style.get(self.mapper_inverse[i].style, 'normal'))

    def clear_selection(self):
        for i in self.selection:
            self.itemconfigure(i, self.style.get(self.mapper_inverse[i].style, 'normal'))

    def wait_selection(self) -> U:
        """Wait until a new item is selected. Similar to `wait_variable`.

        :return U: The userdata pointing to the newly selected item.
        """
        v = IntVar(self)
        t = self.bind('<<Selected>>', lambda _: v.set(1))
        self.wait_variable(v)
        self.unbind('<<Selected>>', t)
        return self.selection_change

    # ------------------------------Drag Scroll------------------------------

    def enable_drag_scroll(self, gain: int = 1):

        def on_drag(e: Event):
            self.scan_dragto(e.x_root, e.y_root, gain=gain)
            self['cursor'] = 'fleur'

        def on_release(_):
            self['cursor'] = 'arrow'

        self.bind('<Button-1>', lambda e: self.scan_mark(e.x_root, e.y_root), add='+')
        self.bind('<B1-Motion>', on_drag, add='+')
        self.bind('<ButtonRelease-1>', on_release, add='+')

# TODO
# The conflict between drag_scroll and selection.

if __name__ == '__main__':
    from tkinter import Tk
    from tkinter.ttk import Button

    root = Tk()

    style = StyleManager()
    style.configure(
        'TLine',
        fill=('gray', 'gray', 'red', 'red'),
        width=(8, 8, 8, 8),
        dash=('-', '-..', '-', '--.--')
    )

    cv = CanvasPlus(root, style)
    cv.pack()
    cv.enable_drag_scroll()

    cv.add_line((0, 0), (100, 100), 1, 'TLine')
    cv.enable_selection_all()

    root.mainloop()