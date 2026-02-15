from __future__ import annotations
from math import isclose

def eq_with_eps[T: tuple[float, ...]](a: T, b: T, eps: float = 1e-7) -> bool:
    assert len(a) == len(b)
    return all(isclose(a_i, b_i, abs_tol=eps) for a_i, b_i in zip(a, b))

def gt_with_eps[T: tuple[float, ...]](a: T, b: T, eps: float = 1e-7) -> bool:
    assert len(a) == len(b)
    for a_i, b_i in zip(a, b):
        if a_i > b_i - eps:
            return True
        if a_i < b_i + eps:
            return False
    return False

def gt_unsafe[T: tuple[float, ...]](a: T, b: T) -> bool:
    assert len(a) == len(b)
    for a_i, b_i in zip(a, b):
        if a_i > b_i:
            return True
        if a_i < b_i:
            return False
    return False

class FloatSeqDict[K: tuple[float, ...], V]:

    def __init__(self, eps: float):
        self._floats: list[K] = []
        self._data: list[V] = []
        self._eps = eps

    @staticmethod
    def from_pair(eps, *pair: tuple[K, V]) -> FloatSeqDict[K, V]:
        d = FloatSeqDict(eps)
        for k, v in pair:
            d[k] = v
        return d

    def __len__(self) -> int:
        return len(self._floats)

    def _search(self, key: K) -> tuple[int, bool]:
        a, b = 0, len(self)
        while a < b:
            mid = (a + b) // 2
            if eq_with_eps(self._floats[mid], key, self._eps):
                return (mid, True)
            elif gt_unsafe(self._floats[mid], key):
                b = mid
            else:
                a = mid + 1
        if a < len(self) and eq_with_eps(self._floats[a], key, self._eps):
            return (a, True)
        return (a, False)

    def __contains__(self, key: K) -> bool:
        return self._search(key)[1]

    def __getitem__(self, key: K):
        index, existed = self._search(key)
        if existed:
            return self._data[index]
        else:
            raise KeyError()

    def __setitem__(self, key: K, value: V):
        index, existed = self._search(key)
        if existed:
            self._data[index] = value
        else:
            self._floats.insert(index, key)
            self._data.insert(index, value)

    def pop_min(self) -> tuple[K, V] | None:
        if len(self) == 0:
            return None
        k = self._floats.pop(0)
        v = self._data.pop(0)
        return (k, v)

    def setdefault(self, key: K, default: V):
        index, existed = self._search(key)
        if not existed:
            self._floats.insert(index, key)
            self._data.insert(index, default)

    def items(self):
        return zip(self._floats, self._data)

    def keys(self):
        return iter(self._floats)

    def values(self):
        return iter(self._data)
