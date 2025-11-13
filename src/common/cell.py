from typing import Callable
from .callback import Callbacks

__all__ = ('Cell', 'RefCell', 'BorrowMut', 'DifferentiableRefCell')

class Cell[T]:

    def __init__(self, value: T):
        self._value = value
        self.on_change = Callbacks[T]()

    def get(self) -> T:
        return self._value

    def set(self, value: T):
        self._value = value
        self.on_change.emit(value)

class RefCell[M, I]:

    def __init__(self, value: M, get_ref: Callable[[M], I]):
        self._value = value
        self._get_ref = get_ref
        self.on_change = Callbacks[I]()

    def borrow(self) -> I:
        return self._get_ref(self._value)

    def borrow_mut(self):
        return BorrowMut(self)

class BorrowMut[M, I]:

    def __init__(self, cell: RefCell[M, I]):
        self._cell = cell

    def __enter__(self):
        return self._cell._value

    def __exit__(self, *_):
        self._cell.on_change.emit(self._cell.borrow())

class DifferentiableRefCell[M, I, D]:

    def __init__(self, value: M, get_ref: Callable[[M], I]):
        self._value = value
        self._get_ref = get_ref
        self.on_change = Callbacks[tuple[I, D]]()

    def borrow(self) -> I:
        return self._get_ref(self._value)

    def unsafe_borrow_mut(self):
        return self._value