from tkinter import Widget, Toplevel
from tkinter.ttk import Label

__all__ = ('bind_tooltip', )

def bind_tooltip(widget: Widget, text: str, *, dx: int = 25, dy: int = 25, delay: int = 500):
    window: Toplevel | None = None
    id: str | None = None

    def create_tip():
        nonlocal window

        if window is not None:
            return

        x, y = widget.winfo_pointerxy()
        window = Toplevel(widget)
        window.overrideredirect(True)
        window.wm_attributes('-alpha', 0.9)
        window.geometry(f'+{x+dx}+{y+dy}')

        Label(
            window,
            text=text, justify='left', padding=5
        ).pack(fill='both', expand=True)

    def destroy_tip():
        nonlocal window
        if window is not None:
            window.destroy()
            window = None

    def unschedule():
        nonlocal id
        if id is not None:
            widget.after_cancel(id)
            id = None

    def schedule():
        nonlocal id
        unschedule()
        id = widget.after(delay, create_tip)

    enter = lambda _: schedule()
    leave = lambda _: (unschedule(), destroy_tip())
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
    widget.bind('<ButtonPress>', leave)