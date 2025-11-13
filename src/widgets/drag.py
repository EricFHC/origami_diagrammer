from tkinter import Event, Widget

__all__ = ('bind_drag', )

def bind_drag(widget: Widget, handle: Widget | None = None):
    start_x = 0
    start_y = 0

    def on_drag_start(e: Event):
        nonlocal start_x, start_y
        start_x = e.x
        start_y = e.y

    def on_dragging(e: Event):
        nonlocal start_x, start_y
        x = widget.winfo_x() - start_x + e.x
        y = widget.winfo_y() - start_y + e.y
        widget.place(x=x, y=y)

    handle = handle or widget
    handle.bind('<Button-1>', on_drag_start)
    handle.bind('<B1-Motion>', on_dragging)

if __name__ == '__main__':
    from random import randint
    from tkinter import Tk
    from tkinter.ttk import Label, Frame, Button

    root = Tk()
    root.title("Dragging Test")
    root.geometry('400x400')

    for i in range(2):
        x = randint(0, 100)
        y = randint(0, 300)
        lbl = Label(root, text=str(i)*6)
        lbl.place(x=x, y=y)
        bind_drag(lbl)

    for i in range(5):
        x = randint(100, 300)
        y = randint(0, 300)
        f = Frame(root)
        Button(f, text="miaow~", state='disabled').pack(side='left', padx=5, pady=5)
        s = Label(f, text="☯", font='-size 20')
        s.pack(side='right')
        f.place(x=x, y=y)
        bind_drag(f, s)

    root.mainloop()
