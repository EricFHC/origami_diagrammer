from typing import Any

from tkinter import Tk, Menu, StringVar, Canvas
from tkinter.ttk import Frame, Radiobutton, Separator, Scrollbar, Label
from tkinter.messagebox import Message

from threading import Thread

from typing import Callable

from widgets import bind_drag
from .components import *

from .process_protocol import *

from common.cell import RefCell
from common.connection import Connection, create_connection

from model.state import State

from pathlib import Path
from ._path import PROJECT_DIRECTORY

from . import assets
from .extension_protocol import ExtensionProtocol
from .process_protocol import CommandProtocol, SafeCommand

import importlib
import importlib.util

class Application(Tk):

    def __init__(self):
        super().__init__()
        self.title("Origami Diagrammer")
        self.geometry('1000x700')
        self.state = State()

    def load(self):
        self.load_images()
        self.setup_ui()
        self.load_extensions()

    def load_images(self):
        path = PROJECT_DIRECTORY / 'assets'
        assets.load(path / 'edit_24.png', 'toolbar::edit')
        assets.load(path / 'view_24.png', 'toolbar::view')

    def load_extensions(self):

        def load_extension(extension: ExtensionProtocol):
            for path, name in extension.assets:
                assets.load(path, name)
            for group, buttons in extension.commands.items():
                command_buttons = []
                for b in buttons:
                    if not isinstance(b.command, CommandProtocol):
                        raise ValueError(f"Command '{b.command}' is invalid.")
                    if not isinstance(b.command, SafeCommand):
                        command = SafeCommand(b.command)
                    else:
                        command = b.command
                    command_buttons.append((b.image, b.tooltip, lambda: self._execute_command(b.tooltip, command)))
                self.command_panel.add(group.image, group.tooltip, *command_buttons)

        try:
            path = PROJECT_DIRECTORY / 'src' / 'extensions'

            if not path.exists:
                raise FileNotFoundError("Cannot find extensions.")

            for item in path.iterdir():
                if item.name.startswith('_') or not item.is_dir():
                    continue

                module_name = f'{path.name}.{item.name}'

                spec = importlib.util.find_spec(module_name)
                if spec is None:
                    continue

                module = importlib.import_module(module_name)
                if not isinstance(module, ExtensionProtocol):
                    raise ValueError(f"Extension '{item}' does not follow the protocol.")

                load_extension(module)
        except (FileNotFoundError, ValueError) as err:
            Message(self, icon='error', type='ok', message=err).show()
        except ImportError as err:
            Message(self, icon='error', type='ok', message="Failed to import extension.").show()

    def setup_ui(self):
        # ------------------------------menu------------------------------
        menu = Menu()

        menu_file = Menu(menu, tearoff=False)
        menu_file.add_command(label="open", accelerator='Ctrl+O')
        menu.add_cascade(label="file", menu=menu_file)

        menu_settings = Menu(menu, tearoff=False)
        menu_settings.add_command(label="settings")
        menu_settings.add_command(label="open setting file")
        menu.add_cascade(label="settings", menu=menu_settings)

        menu_help = Menu(menu, tearoff=False)
        menu_help.add_command(label="doc", accelerator='F1')
        menu_help.add_command(label="publish")
        menu.add_cascade(label="help", menu=menu_help)

        self.configure(menu=menu)
        # ------------------------------toolbar------------------------------
        toolbar = Frame(self)
        toolbar.pack(side='top', fill='x')

        self.var_view = StringVar()
        self.var_view.set('edit')
        self.btn_edit = Radiobutton(toolbar, style='Toolbutton', variable=self.var_view, value='edit', image="toolbar::edit", text='edit', compound='left')
        self.btn_edit.pack(side='left', padx=5, pady=2)
        self.btn_step = Radiobutton(toolbar, style='Toolbutton', variable=self.var_view, value='step', image="toolbar::view", text='steps', compound='left')
        self.btn_step.pack(side='left', padx=5, pady=2)

        Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5, pady=2)

        self.lbl_step = Label(toolbar, text="step: 0")
        self.lbl_step.pack(side='left', padx=5, pady=2)
        # ------------------------------workspace------------------------------
        self.workspace = Frame(self)
        self.workspace.pack(side='bottom', fill='both', expand=True)
        self.workspace.grid_rowconfigure(0, weight=1)
        self.workspace.grid_columnconfigure(0, weight=1)
        # ------------------------------workspace > canvas------------------------------
        self.cv = Canvas(self.workspace, bg='white')
        self.cv.grid(row=0, column=0, sticky='nsew')
        #self.cv.enable_drag_scroll()
        #self.cv.set_state(self.current_state)

        self.srl_y = Scrollbar(self.workspace, orient='vertical', command=self.cv.yview)
        self.cv['yscrollcommand'] = self.srl_y.set
        self.srl_y.grid(row=0, column=1, sticky='ns')

        self.srl_x = Scrollbar(self.workspace, orient='horizontal', command=self.cv.xview)
        self.cv['xscrollcommand'] = self.srl_x.set
        self.srl_x.grid(row=1, column=0, sticky='we')
        # ------------------------------workspace > hint------------------------------
        self.hint_panel = HintPanel(self.workspace)
        self.hint_panel.place(x=300, y=20)
        self.hint_panel.lower()
        self.hint_panel.hand['cursor'] = 'fleur'
        bind_drag(self.hint_panel, self.hint_panel.hand)
        # ------------------------------workspace > parameter panel------------------------------
        self.parameter_panel = ParameterPanel(self.workspace)
        self.parameter_panel.place(x=700, y=300)
        self.parameter_panel.lower()
        self.parameter_panel.lbl_name['cursor'] = 'fleur'
        bind_drag(self.parameter_panel, self.parameter_panel.lbl_name)
        # ------------------------------workspace > commands------------------------------
        self.command_panel = CommandPanel(self.workspace)
        self.command_panel.place(x=20, y=20)

    def _execute_command(self, name: str, command: Callable[[Connection[Data, Any]], None]):
        c1, c2 = create_connection()
        _CommandHandler(self, name, c1).start()
        Thread(target=command, args=(c2, )).start()

class _CommandHandler(Thread):

    def __init__(self, window: Application, name: str, conn: Connection[Any, Data]):
        super().__init__()
        self.window = window
        self.command_name = name
        self.conn = conn

    def _enter(self):
        self.window.command_panel.disable()
        self.window.parameter_panel.set_name(self.command_name)
        self.window.parameter_panel.tkraise()

    def _exit(self):
        self.window.command_panel.enable()
        self.window.parameter_panel.lower()
        self.window.parameter_panel.clear_editor()
        self.window.hint_panel.set(None)

    def run(self):
        self._enter()
        try:
            self.conn.send(self.window.state)
            while r := self.conn.recv():
                if isinstance(r, End) or r is End: break
                elif isinstance(r, RequestParameters): self.handle_parameter_request(r)
                elif isinstance(r, RequestItem): self.handle_item_request(r)
                else: raise RuntimeError("The command thread sent unexpected data.")
        except BaseException as err:
            Message(self.window, icon='info', type='ok', message=f"An un excepted error has occurred. Details:\n{err}").show()
        finally:
            self._exit()

    def handle_parameter_request(self, request: RequestParameters):
        for name, (editor, immediate) in request.parameters.items():
            self.window.parameter_panel.add_editor(name, editor)

            if not immediate: continue
            if not editor.support_wait(): raise RuntimeError()

            v = StringVar()
            t = lambda _: v.set("")
            editor.on_change.bind(t)
            self.window.wait_variable(v)
            editor.on_change.unbind(t)

        self.conn.send(None)

    def handle_item_request(self, request: RequestItem):
        pass