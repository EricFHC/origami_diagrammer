from __future__ import annotations
from typing import Iterable, Iterator, Callable
from itertools import chain, batched

__all__ = ('IteratorWrap', )

class IteratorWrap[T]:

    def __init__(self, source: Iterable[T]):
        self.source = source

    def __iter__(self) -> Iterator[T]:
        return iter(self.source)

    def map[U](self, mapper: Callable[[T], U]) -> IteratorWrap[U]:
        return IteratorWrap(map(mapper, self.source))

    def enumerate(self) -> IteratorWrap[tuple[int, T]]:
        return IteratorWrap(enumerate(self.source))

    def filter(self, filter_fn: Callable[[T], bool]) -> IteratorWrap[T]:
        return IteratorWrap(filter(filter_fn, self.source))

    def chain(self, rhs: Iterable[T]) -> IteratorWrap[T]:
        return IteratorWrap(chain(self.source, rhs))

    def batched(self, n: int = 2) -> IteratorWrap[tuple[T, ...]]:
        return IteratorWrap(batched(self.source, n))

    def flatten(self) -> IteratorWrap:
        return IteratorWrap(chain.from_iterable(self.source))

    def foreach(self, fn: Callable[[T], None]):
        for i in self:
            fn(i)