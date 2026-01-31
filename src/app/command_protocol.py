from typing import Protocol, runtime_checkable, Literal
from dataclasses import dataclass, field
from common import Connection, Option, Some
from widgets import Editor
from model import *

@runtime_checkable
class Command[S, R](Protocol):

    def __call__(self, conn: Connection[S, R]) -> None:
        pass

class CommandCollapse: pass

@dataclass
class SafeCommand[S, R]:

    command: Command[S, R]

    def __call__(self, connection: Connection[S | CommandCollapse, R]):
        try:
            self.command(connection)
        except BaseException as err:
            connection.send(CommandCollapse())

@dataclass
class RequestParameters:

    parameters: dict[str, tuple[Editor, bool]] = field(default_factory=dict)

@dataclass
class RequestItem:

    hint: str = ""
    from_ids: Option[tuple[int, ...]] = Option(None)
    by_type: Option[Literal['vertex', 'line', 'face']] = Option(None)

type ModelEditConnection = Connection[RequestParameters | RequestItem | State, State | VertexId]
type ModelEditCommand = Command[RequestParameters | RequestItem | State, State | VertexId]
type ModelLoadCommand = Command[State, str]