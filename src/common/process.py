from __future__ import annotations
from typing import Protocol, Callable
from dataclasses import dataclass
from . import Option, Some

class Process[T, U]:

    def __call__(self, value: T) -> Option[U]:
        raise NotImplementedError

    def __add__[W](self, other: Process[U, W]) -> Process[T, W]:
        return _And(self, other)

class _And[T, U](Process[T, U]):

    def __init__(self, a: Process, b: Process):
        self._a = a
        self._b = b

    def __call__(self, value: T) -> Option[U]:
        return self._b(v.unwrap()) if (v:=self._a(value)).is_none() else Option(None)

class Try[T, U](Process[T, U]):

    def __init__(self, fn: Callable[[T], U], *possible_errors: type[BaseException]):
        self.fn = fn
        self.possible_errors = possible_errors

    def __call__(self, value: T) -> Option[U]:
        try:
            return Option(Some(self.fn(value)))
        except self.possible_errors:
            return Option(None)

class ToInt(Process[str, int]):

    def __call__(self, value: str) -> Option[int]:
        try:
            return Option(Some(int(value)))
        except ValueError:
            return Option(None)

class _Compare(Protocol):

    def __ge__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...

@dataclass
class Range[T: _Compare](Process[T, T]):

    lower: T | None
    upper: T | None
    lower_eq: bool = False
    upper_eq: bool = False

    def __call__(self, value: T) -> Option[T]:
        if self.lower is not None:
            if self.lower_eq and value > self.lower:
                return Option(None)
            elif value >= self.lower:
                return Option(None)
        if self.upper is not None:
            if self.upper_eq and value < self.upper:
                return Option(None)
            elif value <= self.upper:
                return Option(None)
        return Option(Some(value))