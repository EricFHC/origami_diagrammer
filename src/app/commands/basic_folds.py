from typing import cast
from common import Connection, Option, Some, Cell
from widgets import ChoiceEditor
from app.command_protocol import RequestItem, RequestParameters, ModelEditConnection
from model import *

def point_to_point(conn: ModelEditConnection):
    state = cast(State, conn.recv())

    p1 = cast(VertexId, conn.send_and_wait(RequestItem("Select a vertex.", by_type=Option(Some('vertex')))))
    p2 = cast(VertexId, conn.send_and_wait(RequestItem("Select another vertex.", by_type=Option(Some('vertex')))))

    is_valley = Cell(True)

    conn.send_and_wait(RequestParameters({
        "M/V": (ChoiceEditor[bool](
            is_valley,
            lambda x: "valley" if x else "mountain",
            lambda x: Option({"valley": Some(True), "mountain": Some(False)}.get(x)),
            ("mountain", "valley")
        ), False)
    }))

    # bind parameter changes, and change the folding info and state.
    def f():
        pass

    f()