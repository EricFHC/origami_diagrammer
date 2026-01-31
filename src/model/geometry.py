from __future__ import annotations
from dataclasses import dataclass
from math import hypot
import unittest

class Vec2:

    __slots__ = ('x', 'y')

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f'({self.x:.7f}, {self.y:.7f})'

    def copy(self) -> Vec2:
        return Vec2(self.x, self.y)

    def perp(self) -> Vec2:
        return Vec2(-self.y, self.x)

    def dot(self, rhs: Vec2) -> float:
        return self.x * rhs.x + self.y * rhs.y

    def perp_dot(self, rhs: Vec2) -> float:
        return self.x * rhs.y - self.y * rhs.x

    def length_squared(self) -> float:
        return pow(self.x, 2) + pow(self.y, 2)

    def length(self) -> float:
        return hypot(self.x, self.y)

    def __abs__(self) -> float:
        return hypot(self.x, self.y)

    def __add__(self, rhs: Vec2) -> Vec2:
        return Vec2(self.x + rhs.x, self.y + rhs.y)

    def __sub__(self, rhs: Vec2) -> Vec2:
        return Vec2(self.x - rhs.x, self.y - rhs.y)

    def __mul__(self, rhs: float) -> Vec2:
        return Vec2(self.x * rhs, self.y * rhs)

    def __truediv__(self, rhs: float) -> Vec2:
        return Vec2(self.x / rhs, self.y / rhs)

    def __iadd__(self, rhs: Vec2):
        self.x += rhs.x
        self.y += rhs.y
        return self

    def __isub__(self, rhs: Vec2):
        self.x -= rhs.x
        self.y -= rhs.y
        return self

    def __imul__(self, rhs: float):
        self.x *= rhs
        self.y *= rhs
        return self

    def __itruediv__(self, rhs: float):
        self.x /= rhs
        self.y /= rhs
        return self

@dataclass
class Segment:

    a: Vec2
    b: Vec2

    def intersection(self, other: Segment):
        pass

@dataclass
class Transform:

    a: float
    b: float
    c: float
    d: float
    e: float
    f: float
    g: float
    h: float
    i: float

    @staticmethod
    def identity() -> Transform:
        return Transform(
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        )

    @staticmethod
    def translation(dx: float, dy: float) -> Transform:
        return Transform(
            1.0, 0.0, dx,
            0.0, 1.0, dy,
            0.0, 0.0, 1.0,
        )

    @staticmethod
    def fold_transform(p1: Vec2, p2: Vec2, eps: float = 1e-7):
        n = (p1 - p2).perp()
        length = n.length()
        if length < eps:
            raise ValueError(f'p1 is too close to p2: {p1} and {p2}.')
        n /= length

        # Line: ax + by + c = 0
        a = n.x
        b = n.y
        c = -n.dot(p1)

        return Transform(
            1-2*pow(a, 2), -2*a*b, -2*a*c,
            -2*a*b, 1-2*pow(b, 2), -2*b*c,
            0, 0, 1,
        )

    def mul(self, t: Transform) -> Transform:
        s = self
        return Transform(
            s.a*t.a+s.b*t.d+s.c*t.g, s.a*t.b+s.b*t.e+s.c*t.h, s.a*t.c+s.b*t.f+s.c*t.i,
            s.d*t.a+s.e*t.d+s.f*t.g, s.d*t.b+s.e*t.e+s.f*t.h, s.d*t.c+s.e*t.f+s.f*t.i,
            s.g*t.a+s.h*t.d+s.i*t.g, s.g*t.b+s.h*t.e+s.i*t.h, s.g*t.c+s.h*t.f+s.i*t.i,
        )

    def then(self, t: Transform) -> Transform:
        return t.mul(self)

    def apply_to(self, v: Vec2) -> Vec2:
        """NOTE: The scale factor is ignored, given that it is not used and may unsteady float calculation."""
        return Vec2(
            self.a * v.x + self.b * v.y + self.c,
            self.d * v.x + self.e * v.y + self.f,
        ) # * self.i

class TestTransform(unittest.TestCase):

    def test_mat_multiply(self):
        self.assertEqual(
            Transform(-1, 2, 0, 3, -4, 5, -2, 0, 1)
            .mul(Transform(2, -3, 1, 0, 4, -2, -1, 0, 3)),
            Transform(-2, 11, -5, 1, -25, 26, -5, 6, 1)
        )
        self.assertEqual(
            Transform(1, 2, 3, 4, 5, 6, 7, 8, 9).mul(Transform.identity()),
            Transform(1, 2, 3, 4, 5, 6, 7, 8, 9)
        )

    def test_fold_transform(self):
        self.assertAlmostEqual(Transform.fold_transform(Vec2(0, 1), Vec2(1, 0)).apply_to(Vec2(0, 0)), Vec2(1, 1))
        self.assertAlmostEqual(Transform.fold_transform(Vec2(1, 0), Vec2(0, 3**0.5)).apply_to(Vec2(0, 0)), Vec2(1.5, 0.5*3**0.5))

        t = Transform.fold_transform(Vec2(10, 0), Vec2(10, 1))
        t = t.then(t)
        for v in (Vec2(1, 1), Vec2(10, 0), Vec2(-5, -7), Vec2(20, -9)):
            self.assertAlmostEqual(t.apply_to(v), v)

    def test_multi_transform(self):
        t = Transform(1, 0, 1, 0, 1, 0, 0, 0, 1)
        t2 = Transform.fold_transform(Vec2(10, 0), Vec2(0, 10))
        self.assertAlmostEqual(t.then(t2).apply_to(Vec2(1, 1)), Vec2(9, 8))

if __name__ == '__main__':
    unittest.main()