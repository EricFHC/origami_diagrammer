from typing import Literal, runtime_checkable, Protocol
from dataclasses import dataclass, field
from common import Option
from common.connection import Connection
from widgets import Editor

@dataclass
class RequestParameters:

    parameters: dict[str, tuple[Editor, bool]] = field(default_factory=dict)

@dataclass
class RequestItem:

    hint: str = ""
    from_ids: Option[tuple[int, ...]] = Option(None)
    by_type: Option[Literal['vertex', 'line', 'face']] = Option(None)

class End:
    pass

type Data = RequestParameters | RequestItem | End


@runtime_checkable
class CommandProtocol(Protocol):

    def __call__(self, connection: Connection) -> None:
        pass

@dataclass
class SafeCommand:

    command: CommandProtocol

    def __call__(self, connection: Connection) -> None:
        self.command(connection)
        connection.send(End())

# def point_to_point(conn: Connection):
#     state: DifferentiableRefCell[State, FrozenState, StateDifference] = conn.recv()

#     p1: VertexId = conn.send_and_wait(RequestItem("Select a vertex.", by_type=Option(Some('vertex'))))
#     p2: VertexId = conn.send_and_wait(RequestItem("Select another vertex.", by_type=Option(Some('vertex'))))

#     is_valley = Cell(True)

#     conn.send_and_wait(RequestParameters({
#         "M/V": (ChoiceEditor[bool](
#             is_valley,
#             lambda x: "valley" if x else "mountain",
#             lambda x: Option({"valley": Some(True), "mountain": Some(False)}.get(x)),
#             ("mountain", "valley")
#         ), False)
#     }))

#     # bind parameter changes, and change the folding info and state.
#     def f():
#         pass

#     f()

#     #conn.send(Value[FoldingInfo](FoldingInfo()))
#     conn.send(End())
