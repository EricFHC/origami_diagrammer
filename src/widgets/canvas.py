from typing import TypedDict, NotRequired
from enum import IntFlag
from dataclasses import dataclass
from tkinter import Canvas, Event

__all__ = ('ItemStyleCommon', 'ItemStyleOfState', 'CanvasPlus')

class ItemStyleOption(TypedDict):

    dash: NotRequired[str]
    dashoffset: NotRequired[int]
    fill: NotRequired[str]
    stipple: NotRequired[str]
    width: NotRequired[int]

@dataclass
class ItemStyleCommon:

    dash: str | None = None
    dash_offset: int | None = None
    fill: str | None = None
    stipple: str | None = None
    width: int | None = None
    alpha: float | None = None

    def into_dict(self) -> ItemStyleOption:
        options: ItemStyleOption = {}

        if self.dash is not None:
            options['dash'] = self.dash
            if self.dash_offset is not None:
                options['dashoffset'] = self.dash_offset

        if self.fill is not None:
            options['fill'] = self.fill
        if self.width is not None:
            options['width'] = self.width

        # TODO: Major
        # Implement the alpha filling. (Create a bitmap with PIL.)
        if self.alpha is not None:
            pass
        elif self.stipple is not None:
            options['stipple'] = self.stipple

        return options

@dataclass
class ItemStyleOfState:

    normal: ItemStyleOption
    hover: ItemStyleOption
    selected: ItemStyleOption
    selected_hover: ItemStyleOption

    def auto_complete(self):
        def do(parent: ItemStyleOption, child: ItemStyleOption):
            for key, value in parent.items():
                child.setdefault(key, value) # type: ignore

        self.normal.setdefault('dash', '')
        self.normal.setdefault('fill', 'black')
        self.normal.setdefault('stipple', '')
        self.normal.setdefault('width', 2)

        do(self.normal, self.hover)
        do(self.hover, self.selected)
        do(self.selected, self.selected_hover)

        return self

class CanvasPlus[U](Canvas):

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        self.style: dict[IntFlag, ItemStyleOfState] = {}

        self.mapper: dict[U, int] = {}
        self.mapper_inverse: dict[int, tuple[U, IntFlag]] = {}

        self.permit_user_deselect = False
        self.selection: set[int] = set()
        self._selection_change: int = -1
        self.selection_change: U
        self._init_selection()

    # ------------------------------Draw------------------------------

    def add_point(self, x: float, y: float, r: float, style: IntFlag, userdata: U):
        item_id = self.create_oval(x-r, y-r, x+r, y+r, **self.style[style].normal)
        self.mapper[userdata] = item_id
        self.mapper_inverse[item_id] = (userdata, style)

    def add_line(self, x1: float, y1: float, x2: float, y2: float, style: IntFlag, userdata: U):
        item_id = self.create_line(x1, y1, x2, y2, **self.style[style].normal)
        self.mapper[userdata] = item_id
        self.mapper_inverse[item_id] = (userdata, style)

    def add_face(self, *coords: tuple[float, float], style: IntFlag, userdata: U):
        item_id = self.create_polygon(*coords, **self.style[style].normal)
        self.mapper[userdata] = item_id
        self.mapper_inverse[item_id] = (userdata, style)

    def zoom(self, factor: float):
        """Note: Do not use this method too often, which may cause precise issues."""
        for item in self.mapper_inverse.keys():
            c = self.coords(item)
            tp = self.type(item)
            if tp in ('polygon', 'line'):
                self.coords(item, tuple(map(lambda x: x*factor, c)))
            elif tp == 'oval':
                left, top, right, bottom = c
                x = (left + right) * 0.5 * factor
                y = (top + bottom) * 0.5 * factor
                r_x = (right - left) * 0.5
                r_y = (bottom - top) * 0.5
                self.coords(item, (x-r_x, y-r_y, x+r_x, y+r_y))

    # ------------------------------Selecting------------------------------

    # Bind all methods for selecting.
    def _init_selection(self):
        hover_id = -1

        def on_enter(_):
            nonlocal hover_id
            hover_id = self.find_withtag('current')[0]
            style = self.style[self.mapper_inverse[hover_id][1]]
            if hover_id in self.selection:
                self.itemconfigure(hover_id, **style.selected_hover)
            else:
                self.itemconfigure(hover_id, **style.hover)

        def on_press(_):
            nonlocal hover_id
            # SAFETY
            # Due to the trigger order of events, `hover_id` must point to the item under the mouse.
            self._selection_change = hover_id
            self.selection_change = self.mapper_inverse[hover_id][0]
            style = self.style[self.mapper_inverse[hover_id][1]]
            if hover_id in self.selection:
                if self.permit_user_deselect:
                    self.selection.remove(hover_id)
                    self.itemconfigure(hover_id, **style.hover)
                    self.event_generate('<<Deselect>>', data=hover_id)
            else:
                self.selection.add(hover_id)
                self.itemconfigure(hover_id, **style.selected_hover)
                self.event_generate('<<Select>>', data=hover_id)

        def on_leave(_):
            nonlocal hover_id
            # SAFETY
            # The same as `on_press`.(～￣▽￣)～
            style = self.style[self.mapper_inverse[hover_id][1]]
            if hover_id in self.selection:
                self.itemconfigure(hover_id, **style.selected)
            else:
                self.itemconfigure(hover_id, **style.normal)
            hover_id = -1

        self.tag_bind('selectable', '<Enter>', on_enter)
        self.tag_bind('selectable', '<Leave>', on_leave)
        self.tag_bind('selectable', '<ButtonRelease-1>', on_press)

    def enable_selection_of_style(self, style: IntFlag):
        for i, d in self.mapper_inverse.items():
            if d[1] in style:
                self.addtag_withtag('selectable', i)

    def disable_selection_of_style(self, style: IntFlag):
        for i, d in self.mapper_inverse.items():
            if d[1] in style:
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
        self.itemconfigure(i, **self.style[self.mapper_inverse[i][1]].selected)

    def deselect(self, item: U):
        i = self.mapper[item]
        if i not in self.selection:
            return
        self.selection.remove(i)
        self.itemconfigure(i, **self.style[self.mapper_inverse[i][1]].normal)

    def clear_selection(self):
        for i in self.selection:
            self.itemconfigure(i, **self.style[self.mapper_inverse[i][1]].normal)

    def wait_selection(self) -> U:
        """Wait until a new item is selected. Similar to `wait_variable`.

        :return U: The userdata of the newly selected item.
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

# TODO: Minor
# The conflict between drag_scroll and selection.

if __name__ == '__main__':
    from tkinter import Tk, Checkbutton, Frame, IntVar
    from enum import auto

    class Styles(IntFlag):

        Empty = 0

        Point = auto()
        Face = auto()

        RawEdge = auto()
        Mountain = auto()
        Valley = auto()
        Crease = Mountain | Valley
        Line = Crease | RawEdge

    root = Tk()

    frame = Frame(root)
    frame.pack(side='left', anchor='n', padx=5, pady=5)

    var_point = IntVar()
    chk_point = Checkbutton(frame, text="point", variable=var_point, onvalue=Styles.Point, offvalue=Styles.Empty)
    chk_point.pack(side='top', anchor='w')

    var_crease = IntVar()
    var_m = IntVar()
    var_v = IntVar()
    chk_crease = Checkbutton(frame, text="crease", variable=var_crease, onvalue=Styles.Crease, offvalue=Styles.Empty)
    chk_m = Checkbutton(frame, text="mountain", variable=var_m, onvalue=Styles.Mountain, offvalue=Styles.Empty)
    chk_v = Checkbutton(frame, text="valley", variable=var_v, onvalue=Styles.Valley, offvalue=Styles.Empty)
    chk_crease.pack(side='top', anchor='w')
    chk_m.pack(side='top', anchor='w')
    chk_v.pack(side='top', anchor='w')

    var_face = IntVar()
    chk_face = Checkbutton(frame, text="face", variable=var_face, onvalue=Styles.Face, offvalue=Styles.Empty)
    chk_face.pack(side='top', anchor='w')

    cv = CanvasPlus(root, background='white')
    cv.pack(fill='both', expand=True, padx=5, pady=5)

    # TODO: A confusing bug
    # When width in normal being set, the program seems stuck.
    cv.style[Styles.RawEdge] = ItemStyleOfState(
        normal=ItemStyleCommon().into_dict(),
        hover=ItemStyleCommon(dash='--').into_dict(),
        selected=ItemStyleCommon(fill='purple').into_dict(),
        selected_hover=ItemStyleCommon().into_dict(),
    ).auto_complete()
    cv.style[Styles.Mountain] = ItemStyleOfState(
        normal=ItemStyleCommon(fill='red').into_dict(),
        hover=ItemStyleCommon(dash='--').into_dict(),
        selected=ItemStyleCommon(fill='purple').into_dict(),
        selected_hover=ItemStyleCommon().into_dict(),
    ).auto_complete()
    cv.style[Styles.Face] = ItemStyleOfState(
        normal=ItemStyleCommon(fill='').into_dict(),
        hover=ItemStyleCommon(fill='green', stipple='gray50').into_dict(),
        selected=ItemStyleCommon().into_dict(),
        selected_hover=ItemStyleCommon().into_dict(),
    ).auto_complete()

    cv.enable_drag_scroll()
    cv.permit_user_deselect = True

    # Mind the order of adding, which determines the order of mouse checking. This may be improved in future work.
    cv.add_line(0, 0, 0, 100, Styles.RawEdge, 0)
    cv.add_line(0, 100, 100, 100, Styles.RawEdge, 1)
    cv.add_line(100, 100, 100, 0, Styles.RawEdge, 2)
    cv.add_line(100, 0, 0, 0, Styles.RawEdge, 3)

    cv.add_face(0, 0, 100, 0, 100, 100, style=Styles.Face, userdata=5)
    cv.add_face(0, 0, 0, 100, 100, 100, style=Styles.Face, userdata=6)

    cv.add_line(0, 0, 100, 100, Styles.Mountain, 4)

    selectable_styles = Styles.Empty
    def set_selection():
        global selectable_styles
        cv.disable_selection_of_style(selectable_styles)
        selectable_styles = Styles.Empty | var_point.get() | var_crease.get() | var_m.get() | var_v.get() | var_face.get()
        cv.enable_selection_of_style(selectable_styles)

    chk_point['command'] = set_selection
    chk_crease['command'] = set_selection
    chk_m['command'] = set_selection
    chk_v['command'] = set_selection
    chk_face['command'] = set_selection

    root.mainloop()