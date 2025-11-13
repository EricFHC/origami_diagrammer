from threading import Condition
from . import Option, Some, Cell

__all__ = ('create_connection', 'Connection')

class Connection[S, R]:

    def __init__(self, condition: Condition, var_to_send: Cell[Option[S]], var_to_recv: Cell[Option[R]]):
        self._condition = condition
        self._var_to_send = var_to_send
        self._var_to_recv = var_to_recv

    def send(self, data: S):
        with self._condition:
            while not self._var_to_send.get().is_none():
                self._condition.wait()
            self._condition.notify()
            self._var_to_send.set(Option(Some(data)))

    def recv(self) -> R:
        with self._condition:
            while self._var_to_recv.get().is_none():
                self._condition.wait()
            self._condition.notify()
            r = self._var_to_recv.get().unwrap()
            self._var_to_recv.set(Option(None))
            return r

    def send_and_wait(self, data: S) -> R:
        self.send(data)
        return self.recv()

def create_connection[A, B]() -> tuple[Connection[A, B], Connection[B, A]]:
    condition = Condition()
    a: Cell[Option[A]] = Cell(Option(None))
    b: Cell[Option[B]] = Cell(Option(None))

    return (
        Connection(condition, a, b),
        Connection(condition, b, a)
    )