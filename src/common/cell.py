from .callback import Callbacks

__all__ = ('Cell', )

class Cell[T]:

    def __init__(self, value: T):
        self._value = value
        self.on_change = Callbacks[T]()

    def get(self) -> T:
        return self._value

    def set(self, value: T):
        self._value = value
        self.on_change.emit(value)
