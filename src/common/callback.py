from typing import Callable, Any

__all__ = ('Callbacks', )

class Callbacks[T]:

    def __init__(self):
        self._callbacks = set[Callable[[T], Any]]()

    def emit(self, value: T):
        for c in self._callbacks:
            c(value)

    def bind(self, callback: Callable[[T], Any]):
        self._callbacks.add(callback)

    def unbind(self, callback: Callable[[T], Any]):
        self._callbacks.remove(callback)