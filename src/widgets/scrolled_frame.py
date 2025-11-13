from tkinter import Pack, Grid, Place
from tkinter.ttk import Frame, Scrollbar

__all__ = ('ScrolledFrame', )

class ScrolledFrame(Frame):

    def __init__(self, parent=None, height=200, width=300, **kwargs):
        self.container = Frame(parent, borderwidth=0, width=width, height=height)
        self.container.propagate(False)

        self.scroll_y = Scrollbar(self.container, orient='vertical', command=self.yview)
        self.scroll_y.pack(side='right', fill='y')

        f = Frame(self.container)
        f.pack(fill='both', expand=True)

        super().__init__(f, **kwargs)
        self.place(rely=0.0, relwidth=1.0)

        self.container.bind('<Configure>', lambda _: self.yview())
        self.container.bind('<Map>', lambda _: self.yview(), add='+')
        self.bind('<<MapChild>>', lambda _: self.winfo_ismapped() and self.yview(), add='+')

        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        for method in methods:
            if any(t in method for t in ['pack', 'grid', 'place']):
                setattr(self, f"content_{method}", getattr(self, method))
                setattr(self, method, getattr(self.container, method))

    def yview(self, *args):
        if not args:
            first, _ = self.scroll_y.get()
            self.yview_moveto(fraction=first)
        elif args[0] == 'moveto':
            self.yview_moveto(fraction=float(args[1]))
        elif args[0] == 'scroll':
            self.yview_scroll(number=int(args[1]), what=args[2])
        else:
            return

    def yview_moveto(self, fraction: float):
        base, thumb = self._measures()
        if fraction < 0:
            first = 0.0
        elif (fraction + thumb) > 1:
            first = 1 - thumb
        else:
            first = fraction
        self.scroll_y.set(first, first + thumb)
        self.content_place(rely=-first * base)

    def yview_scroll(self, number: int, what: str):
        first, _ = self.scroll_y.get()
        fraction = (number / 100) + first
        self.yview_moveto(fraction)

    def _measures(self) -> tuple[float, float]:
        outer = self.container.winfo_height()
        inner = max([self.winfo_height(), outer])
        base = inner / outer
        if inner == outer:
            thumb = 1.0
        else:
            thumb = outer / inner
        return base, thumb

if __name__ == '__main__':
    import this
    import codecs
    from tkinter import Tk
    from tkinter.ttk import Label, Separator

    root = Tk()
    root.title("Scrolled frame Test")
    root.geometry('600x600')

    f = ScrolledFrame(root)
    f.pack(fill='both', expand=True)

    for l in this.s.split('\n'):
        Label(f, text=l).pack(anchor='w', padx=5, pady=5)

    Separator(f, orient='horizontal').pack(fill='x', padx=5, pady=5)

    for l in codecs.decode(this.s, 'rot13').split('\n'):
        Label(f, text=l).pack(anchor='w', padx=5, pady=5)

    root.mainloop()