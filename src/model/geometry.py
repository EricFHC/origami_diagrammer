from __future__ import annotations
from dataclasses import dataclass
from math import hypot
import unittest

@dataclass(frozen=True)
class Vec2:

    x: float
    y: float

    def __repr__(self) -> str:
        return f'({self.x:.7f}, {self.y:.7f})'

    # def copy(self) -> Vec2:
    #     return Vec2(self.x, self.y)

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

    # def __iadd__(self, rhs: Vec2):
    #     self.x += rhs.x
    #     self.y += rhs.y
    #     return self

    # def __isub__(self, rhs: Vec2):
    #     self.x -= rhs.x
    #     self.y -= rhs.y
    #     return self

    # def __imul__(self, rhs: float):
    #     self.x *= rhs
    #     self.y *= rhs
    #     return self

    # def __itruediv__(self, rhs: float):
    #     self.x /= rhs
    #     self.y /= rhs
    #     return self

@dataclass
class Segment:

    a: Vec2
    b: Vec2

    def intersection(self, other: Segment, eps: float = 1e-7) -> Vec2 | type[Segment] | None:
        a = self.a
        b = self.b
        c = other.a
        d = other.b

        if ((max(a.x, b.x) < min(c.x, d.x) or min(a.x, b.x) > max(c.x, d.x)) and
            (max(a.y, b.y) < min(c.y, d.y) or min(a.y, b.y) > max(c.y, d.y))):
            return None

        ab = b - a
        ac = c - a
        ad = d - a
        if ab.perp_dot(ac) * ab.perp_dot(ad) > eps:
            return None

        cd = d - c
        ca = a - c
        cb = b - c
        if cd.perp_dot(ca) * cd.perp_dot(cb) > eps:
            return None

        denominator = ab.perp_dot(cd)

        if abs(denominator) < eps:
            return Segment

        u = ac.perp_dot(cd) / denominator
        return a + ab * u

    def intersection_with_axis_x(self, y: float, eps: float = 1e-7) -> float | type[Segment] | None:
        if y < min(self.a.y, self.b.y) or y > max(self.a.y, self.b.y):
            return None
        if abs(self.a.y - self.b.y) < eps:
            return Segment
        d = self.a.y - y
        if abs(d) < eps:
            return self.a.x
        u = d / (self.a.y - self.b.y)
        return self.a.x - u * (self.a.x - self.b.x)

class TestSegment(unittest.TestCase):

    def test_intersection(self):
        r = Segment(Vec2(1, 0), Vec2(0, 1)).intersection(Segment(Vec2(0, 0), Vec2(1, 1)))
        self.assertTrue(isinstance(r, Vec2))
        assert isinstance(r, Vec2)
        self.assertAlmostEqual(r, Vec2(0.5, 0.5))

        r = Segment(Vec2(0, 0), Vec2(10, 10)).intersection(Segment(Vec2(8, 8), Vec2(20, 20)))
        self.assertIs(r, Segment)

        r = Segment(Vec2(10, 10), Vec2(5, 5)).intersection(Segment(Vec2(7, 6), Vec2(10, 6)))
        self.assertIsNone(r)

        r = Segment(Vec2(0, 0), Vec2(10, 10)).intersection(Segment(Vec2(10, 10), Vec2(20, 5)))
        assert isinstance(r, Vec2)
        self.assertIsInstance(r, Vec2)
        self.assertAlmostEqual(r, Vec2(10, 10))

        r = Segment(Vec2(0, 0), Vec2(10, 10)).intersection_with_axis_x(2.0)
        assert isinstance(r, float)
        self.assertTrue(isinstance(r, float))
        self.assertAlmostEqual(r, 2.0)

        r = Segment(Vec2(10, 0), Vec2(0, 10)).intersection_with_axis_x(4.0)
        assert isinstance(r, float)
        self.assertTrue(isinstance(r, float))
        self.assertAlmostEqual(r, 6.0)

        r = Segment(Vec2(0, 0), Vec2(10, 0)).intersection_with_axis_x(0)
        self.assertIs(r, Segment)

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