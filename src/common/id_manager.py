__all__ = ('IdManager', )

class IdManager:

    def __init__(self):
        self._count = 0

    def new(self):
        self._count += 1
        return self._count