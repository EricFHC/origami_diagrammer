__all__ = ('Some', 'Option')

class Some[T]:

    __slots__ = 'x'
    __match_args__ = 'x'

    def __init__(self, x: T):
        self.x = x

class Option[T]:

    __slots__ = 'x'
    __match_args__ = 'x'

    def __init__(self, x: Some[T] | None):
        self.x = x

    def is_none(self) -> bool:
        return self.x is None

    def unwrap(self) -> T:
        if self.x is None:
            raise RuntimeError()
        return self.x.x

    def unwrap_or(self, default: T) -> T:
        return default if self.is_none() else self.unwrap()