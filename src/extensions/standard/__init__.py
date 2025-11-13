from pathlib import Path
from .. import dependencies as dpn

name = "Standard Extension"

path = Path(__file__).resolve().parent / 'basic_fold'

assets = [(path / f'{i}.png', f"basic_fold::{i}") for i in range(1, 8)]

commands = {
    dpn.CommandGroup("basic_fold::1", "7 basic folds"): [
        dpn.CommandButton(
            "basic_fold::1",
            "Fold a line through two points.",
            print
        ),
        dpn.CommandButton(
            "basic_fold::2",
            "Fold a point to another point.",
            print
        )
    ]
}

        #     (
        #         "basic_fold::3",
        #         "Fold a line to another line.",
        #         lambda: self._execute_command("Line to Line", line_to_line)
        #     ),
        #     (
        #         "basic_fold::4",
        #         "",
        #         lambda: self._execute_command("", perpendicular_to_line_through_point)
        #     ),
        #     ("basic_fold::5", "", print),
        #     ("basic_fold::6", "", print),
        #     ("basic_fold::7", "", print)