from typing import cast
import json
import asyncio
from model.state import fold_file

__all__ = ('load_fold_file_cp', )

async def load_fold_file_cp(path: str) -> asyncio.Future[fold_file.DCEL[None, fold_file.LineType, None]]:
    with open(path) as file:
        data = cast(fold_file.FoldFile, json.load(file))

    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, fold_file.into_crease_pattern, data)