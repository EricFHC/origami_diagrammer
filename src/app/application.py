from typing import Generator, Any, overload, Literal

from ._path import PROJECT_DIRECTORY

from tkinter import Tk, Menu, StringVar
from tkinter.ttk import Frame, Radiobutton, Separator, Scrollbar, Label, Notebook
from tkinter import Frame
from tkinter.messagebox import Message
from tkinter import filedialog

from . import assets
import ctypes
from .styling import set_style

from threading import Thread
import asyncio
from asyncio import Future
from common.connection import Connection, create_connection
from .command_protocol import *
from logging import Logger

from widgets import bind_drag
from widgets.editor import Editor
from .components import *

from model.state import definition as md
from .commands import basic_folds, file_operations

class Application(Tk):

    def __init__(self):
        super().__init__()
        self.title("Origami Diagrammer")
        self.geometry('1000x700')
        self.command_runner = _CommandRunner(self)

    def set_high_dip(self):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        scale_factor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
        self.tk.call('tk', 'scaling', scale_factor/75)

    def load(self):
        self.set_high_dip()
        self.load_images()
        set_style()

        self.setup_ui()
        self.hint_panel1.push_message("MAIN")
        self.hint_panel2.push_message("ready")

        self.protocol('WM_DELETE_WINDOW', self.exit)
        self.command_runner.start()

    def exit(self):
        self.destroy()

    def load_images(self):
        path = PROJECT_DIRECTORY / 'assets'
        assets.load(path / 'edit_24.png', 'toolbar::edit')
        assets.load(path / 'view_24.png', 'toolbar::view')
        for i in range(1, 8):
            assets.load(path / 'basic_fold' / f'{i}.png', f'basic_folds::{i}')

    # def load_extensions(self):

    #     def load_extension(extension: ExtensionProtocol):
    #         for path, name in extension.assets:
    #             assets.load(path, name)
    #         for group, buttons in extension.commands.items():
    #             command_buttons = []
    #             for b in buttons:
    #                 if not isinstance(b.command, CommandProtocol):
    #                     raise ValueError(f"Command '{b.command}' is invalid.")
    #                 command_buttons.append((b.image, b.tooltip, lambda: self._execute_command(b.tooltip, b.command)))
    #             self.command_panel.add(group.image, group.tooltip, *command_buttons)

    #     try:
    #         path = PROJECT_DIRECTORY / 'src' / 'extensions'

    #         if not path.exists:
    #             raise FileNotFoundError("Cannot find extensions.")

    #         for item in path.iterdir():
    #             if item.name.startswith('_') or not item.is_dir():
    #                 continue

    #             module_name = f'{path.name}.{item.name}'

    #             spec = importlib.util.find_spec(module_name)
    #             if spec is None:
    #                 continue

    #             module = importlib.import_module(module_name)
    #             if not isinstance(module, ExtensionProtocol):
    #                 raise ValueError(f"Extension '{item}' does not follow the protocol.")

    #             load_extension(module)
    #     except (FileNotFoundError, ValueError) as err:
    #         Message(self, icon='error', type='ok', message=err).show()
    #     except ImportError as err:
    #         Message(self, icon='error', type='ok', message="Failed to import extension.").show()

    def setup_ui(self):
        # ------------------------------menu------------------------------
        menu = Menu()

        menu_file = Menu(menu, tearoff=False)
        menu_file.add_command(label="open", accelerator='Ctrl+O')
        menu_from = Menu(menu_file, tearoff=False)
        menu_from.add_command(label="fold file", command=self.load_fold_file)
        menu_file.add_cascade(label="from", menu=menu_from)
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
        self.workspace = Notebook(self, style='workspace.TNotebook')
        self.workspace.pack(side='top', fill='both', expand=True)

        self.frm_edit = Frame(self.workspace)
        self.setup_ui_edit(self.frm_edit)
        self.workspace.add(self.frm_edit, sticky='nsew')
        #---------------------------------------- statusbar ----------------------------------------
        statusbar = Frame(self)
        statusbar.pack(side='bottom', fill='x')

        self.hint_panel1 = HintPanel(statusbar)
        self.hint_panel1.pack(side='left', padx=2, pady=2)
        self.hint_panel2 = HintPanel(statusbar)
        self.hint_panel2.pack(side='left', padx=2, pady=2)

    def setup_ui_edit(self, frm: Frame):
        # ------------------------------canvas------------------------------
        frm.grid_rowconfigure(0, weight=1)
        frm.grid_columnconfigure(0, weight=1)
        self.cv = FoldedStateRender(frm, bg='white')
        self.cv.grid(row=0, column=0, sticky='nsew')
        self.cv.enable_drag_scroll()

        # self.srl_y = Scrollbar(self.workspace, orient='vertical', command=self.cv.yview)
        # self.cv['yscrollcommand'] = self.srl_y.set
        # self.srl_y.grid(row=0, column=1, sticky='ns')

        # self.srl_x = Scrollbar(self.workspace, orient='horizontal', command=self.cv.xview)
        # self.cv['xscrollcommand'] = self.srl_x.set
        # self.srl_x.grid(row=1, column=0, sticky='we')

        self.cv_cp = CreasePatternRender(self.cv, width='5c', height='5c')
        self.cv_cp.pack(side='top', anchor='e', padx=5, pady=5)
        # ------------------------------parameter panel------------------------------
        self.parameter_panel = ParameterPanel(frm)
        self.parameter_panel.place(x=700, y=300)
        self.parameter_panel.lower()
        self.parameter_panel.lbl_name['cursor'] = 'fleur'
        bind_drag(self.parameter_panel, self.parameter_panel.lbl_name)
        # ------------------------------commands------------------------------
        self.command_panel = CommandPanel(frm)
        self.command_panel.place(x=20, y=20)

        self.command_panel.add(
            "basic_folds::1", "7 basic folds",
            (
                "basic_folds::2",
                "fold a point to point",
                lambda: self.command_runner.run_command(basic_folds.point_to_point),
            )
        )

    def load_fold_file(self):
        path = filedialog.askopenfilename(parent=self, title="Pick a fold file", filetypes=[('fold file', '*.fold')])
        if not path:
            return
        async def command():
            result = await file_operations.load_fold_file_cp(path)
            cp = await result
            self.cv.delete('all')
            self.cv.load_crease_pattern(cp)
            self.cv.zoom(400)
            self.cv.enable_selection_of_style(FoldedStateStyle.FaceWhite)
            self.cv_cp.delete('all')
            self.cv_cp.load_crease_pattern(cp)
            self.cv_cp.adjust_to_size(5, 5)
        asyncio.run_coroutine_threadsafe(command(), self.command_runner.loop)

class _CommandRunner(Thread):

    def __init__(self, app: Application):
        super().__init__(daemon=True)
        self.app = app
        self.handler = _AppCommandHandler(app)

    def run(self):
        self.loop = asyncio.new_event_loop()
        self.loop.run_forever()

    def run_command[T](self, command: Command[T]):
        async def task():
            self.enter()
            res = await command(self.handler)
            self.exit()
        asyncio.run_coroutine_threadsafe(task(), self.loop)

    def enter(self):
        self.app.hint_panel1.push_message("COMMAND")
        self.app.hint_panel2.push_message("")
        self.app.command_panel.disable()

    def exit(self):
        self.app.hint_panel1.push_message("MAIN")
        self.app.command_panel.enable()

class _AppCommandHandler:

    def __init__(self, app: Application):
        self.app = app

    def register_logger(self, logger: Logger):
        pass

    async def request_parameters(self, request: dict[str, tuple[Editor, bool]]) -> Future[None]:
        def task():
            for name, (editor, immediate) in request.items():
                self.app.parameter_panel.add_editor(name, editor)

                if not immediate: continue
                if not editor.support_wait(): raise RuntimeError()

                v = StringVar()
                t = lambda _: v.set("")
                editor.on_change.bind(t)
                self.app.wait_variable(v)
                editor.on_change.unbind(t)

        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, task)

    @overload
    async def request_item_from_ids(self, hint: str, ids: tuple[md.VertexId, ...]) -> Future[md.VertexId]: ...

    @overload
    async def request_item_from_ids(self, hint: str, ids: tuple[md.EdgeId, ...]) -> Future[md.EdgeId]: ...

    @overload
    async def request_item_from_ids(self, hint: str, ids: tuple[md.FaceId, ...]) -> Future[md.FaceId]: ...

    async def request_item_from_ids(self, hint: str, ids: tuple[md.VertexId | md.EdgeId | md.FaceId, ...]) -> Future:
        def task():
            self.app.hint_panel2.push_message(hint)
            self.app.cv.enable_selection(*ids)
            id = self.app.cv.wait_selection()
            self.app.cv.disable_selection_all()
            return id

        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, task)

    @overload
    async def request_item_by_type(self, hint: str, tp: Literal['vertex']) -> Future[md.VertexId]: ...

    @overload
    async def request_item_by_type(self, hint: str, tp: Literal['line']) -> Future[md.EdgeId]: ...

    @overload
    async def request_item_by_type(self, hint: str, tp: Literal['face']) -> Future[md.FaceId]: ...

    async def request_item_by_type(self, hint: str, tp: Literal['vertex', 'line', 'face']) -> Future:
        def task():
            self.app.hint_panel2.push_message(hint)
            self.app.cv.enable_selection_of_style({
                'vertex': FoldedStateStyle.Vertex,
                'line': FoldedStateStyle.Crease,
                'face': FoldedStateStyle.Face
            }[tp])
            id = self.app.cv.wait_selection()
            self.app.cv.disable_selection_all()
            return id

        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, task)