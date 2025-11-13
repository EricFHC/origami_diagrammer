from typing import Callable

__all__ = ('Callbacks', )

class Callbacks[T]:

    def __init__(self):
        self._callbacks = set[Callable[[T],None]]()

    def emit(self, value: T):
        for c in self._callbacks:
            c(value)

    def bind(self, callback: Callable[[T], None]):
        self._callbacks.add(callback)

    def unbind(self, callback: Callable[[T], None]):
        self._callbacks.remove(callback)