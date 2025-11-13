# from __future__ import annotations
# from typing import Callable, Concatenate, Literal

# from tkinter import Canvas, Event

# from geometry import Vec2
# from common import IdManager

# __all__ = ('Anchor', 'CanvasPlus')

# _anchor_id_manager = IdManager()

# class Anchor:

#     def __init__(self, cv: Canvas, x: int, y: int, scale: int):
#         self.cv = cv
#         self._x = x
#         self._y = y
#         self._scale = scale
#         self._tag = f"#{_anchor_id_manager.new()}"

#         self._min_size = 100

#         self._handler = -1
#         self._rect = -1

#     def transform_coord(self, v: Vec2) -> Vec2:
#         return round(Vec2((v.x), -(v.y)) * self._scale + Vec2(self._x, self._y))

#     def move(self, dx: int, dy: int):
#         self._x += dx
#         self._y += dy
#         self.cv.move(self._tag, dx, dy)
#         if self._handler != -1:
#             self.cv.move(self._handler, dx, dy)
#         if self._rect != -1:
#             self.cv.move(self._rect, dx, dy)

#     def move_to(self, x: int, y: int):
#         self.move(x-self._x, y-self._y)

#     def clear(self):
#         self.cv.delete('all')

#     @staticmethod
#     def _wrap[**P](fn: Callable[Concatenate[Anchor, P], int]) -> Callable[Concatenate[Anchor, P], int]:
#         def inner(self: Anchor, *args: P.args, **kwargs: P.kwargs) -> int:
#             tags: tuple[str, ...] = kwargs.get('tags', ()) # type: ignore
#             tags += (self._tag, )
#             kwargs.update(tags=tags)
#             i = fn(self, *args, **kwargs)
#             self._update_drag_rect()
#             return i
#         return inner

#     @_wrap
#     def draw_point(self, v: Vec2, r: int, **kwargs):
#         v = self.transform_coord(v)
#         return self.cv.create_oval(v.x - r, v.y - r, v.x + r, v.y + r, **kwargs)

#     @_wrap
#     def draw_line(self, v1: Vec2, v2: Vec2, **kwargs):
#         v1 = self.transform_coord(v1)
#         v2 = self.transform_coord(v2)
#         return self.cv.create_line(v1.x, v1.y, v2.x, v2.y, **kwargs)

#     @_wrap
#     def draw_poly(self, *vs: Vec2, **kwargs):
#         vs = tuple(map(self.transform_coord, vs))
#         return self.cv.create_polygon(*vs, **kwargs)

#     def enable_drag(self):
#         x1, y1, _, _ = self.cv.bbox(self._tag)
#         self._handler = self.cv.create_text(x1-25, y1-25, text="※",  font='-size 20')

#         def on_click(_):
#             if self._rect == -1:
#                 self._create_drag_rect()
#             else:
#                 self._delete_drag_rect()

#         self.cv.tag_bind(self._handler, '<Button-1>', on_click)

#     def _create_drag_rect(self):
#         self.cv.tkraise(self._tag)
#         self._rect = self.cv.create_rectangle(
#             0, 0, 0, 0,
#             width=2, outline="green", dash="-",
#             fill="gray", stipple='gray25'
#         )
#         self._update_drag_rect()

#         x_prev, y_prev = 0, 0

#         def on_press(e: Event):
#             nonlocal x_prev, y_prev
#             x_prev = e.x
#             y_prev = e.y

#         def on_drag(e: Event):
#             nonlocal x_prev, y_prev
#             self.move(e.x - x_prev, e.y-y_prev)
#             self._update_drag_rect()
#             x_prev = e.x
#             y_prev = e.y

#         self.cv.tag_bind(self._rect, '<Button-1>', on_press)
#         self.cv.tag_bind(self._rect, '<B1-Motion>', on_drag)

#     def _delete_drag_rect(self):
#         self.cv.delete(self._rect)
#         self._rect = -1

#     def _update_drag_rect(self):
#         x1, y1, x2, y2 = self.cv.bbox(self._tag)
#         if self._handler != -1:
#             self.cv.coords(self._handler, x1-25, y1-25)
#         if self._rect != -1:
#             self.cv.coords(self._rect, x1-10, y1-10, x2+10, y2+10)

# class CanvasPlus(Canvas):

#     def enable_drag_scroll(self, gain: int = 1):
#         def on_drag(e: Event):
#             self.scan_dragto(e.x_root, e.y_root, gain=gain)
#             self['cursor'] = 'fleur'
#         def on_release(_):
#             self['cursor'] = 'arrow'
#         self.bind('<Button-1>', lambda e: self.scan_mark(e.x_root, e.y_root), add='+')
#         self.bind('<B1-Motion>', on_drag, add='+')
#         self.bind('<ButtonRelease-1>', on_release, add='+')