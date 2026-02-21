from typing import Protocol, runtime_checkable, Literal, overload, Callable, Awaitable, Coroutine, Any
from dataclasses import dataclass, field
from asyncio import Future
from logging import Logger
from common import Connection, Option, Some
from widgets import Editor
from model.state import definition as d

__all__ = ('CommandHandler', 'Command')

class CommandHandler(Protocol):

    def register_logger(self, logger: Logger): ...

    @overload
    async def request_item_by_type(self, hint: str, tp: Literal['vertex']) -> Future[d.VertexId]: ...

    @overload
    async def request_item_by_type(self, hint: str, tp: Literal['line']) -> Future[d.EdgeId]: ...

    @overload
    async def request_item_by_type(self, hint: str, tp: Literal['face']) -> Future[d.FaceId]: ...

    async def request_item_by_type(self, hint: str, tp: Literal['vertex', 'line', 'face']) -> Future: ...

    @overload
    async def request_item_from_ids(self, hint: str, ids: tuple[d.VertexId, ...]) -> Future[d.VertexId]: ...

    @overload
    async def request_item_from_ids(self, hint: str, ids: tuple[d.EdgeId, ...]) -> Future[d.EdgeId]: ...

    @overload
    async def request_item_from_ids(self, hint: str, ids: tuple[d.FaceId, ...]) -> Future[d.FaceId]: ...

    async def request_item_from_ids(self, hint: str, ids) -> Future: ...

    async def request_parameters(self, request: dict[str, tuple[Editor, bool]]) -> Future[None]: ...

type Command[T] = Callable[[CommandHandler], Coroutine]