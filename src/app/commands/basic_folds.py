from typing import cast
from common import Connection, Option, Some, Cell
from widgets import ChoiceEditor
from app.command_protocol import CommandHandler
from model.state.definition import State, VertexId

async def point_to_point(handler: CommandHandler):
    #state = cast(State, conn.recv())

    p1 = await handler.request_item_by_type("Select a vertex.", 'vertex')
    p2 = await handler.request_item_by_type("Select another vertex.", 'vertex')

    is_valley = Cell(True)

    await handler.request_parameters({
        "M/V": (ChoiceEditor[bool](
            is_valley,
            lambda x: "valley" if x else "mountain",
            lambda x: Option({"valley": Some(True), "mountain": Some(False)}.get(x)),
            ("mountain", "valley")
        ), False)
    })

    # bind parameter changes, and change the folding info and state.
    def f():
        pass

    f()