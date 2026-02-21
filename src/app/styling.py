from tkinter.ttk import Style

def set_style():
    s = Style()

    s.configure('.', font=('Comic Sans MS', 12))

    s.layout('workspace.TNotebook.Tab', [])