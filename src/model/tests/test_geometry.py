from model.geometry import *
from pytest import approx

class TestSegment:

    def test_intersection(self):
       r = Segment(Vec2(1, 0), Vec2(0, 1)).intersection(Segment(Vec2(0, 0), Vec2(1, 1)))
       assert isinstance(r, Vec2)
       assert r == approx(Vec2(0.5, 0.5))

       r = Segment(Vec2(0, 0), Vec2(10, 10)).intersection(Segment(Vec2(8, 8), Vec2(20, 20)))
       assert r is Segment

       r = Segment(Vec2(10, 10), Vec2(5, 5)).intersection(Segment(Vec2(7, 6), Vec2(10, 6)))
       assert r is None

       r = Segment(Vec2(0, 0), Vec2(10, 10)).intersection(Segment(Vec2(10, 10), Vec2(20, 5)))
       assert isinstance(r, Vec2)
       assert r == approx(Vec2(10, 10))

       r = Segment(Vec2(1, 6), Vec2(4, 3)).intersection(Segment(Vec2(2, 2), Vec2(6, 2)))
       assert r is None

    def test_intersection_with_axis_x(self):
       r = Segment(Vec2(0, 0), Vec2(10, 10)).intersection_with_axis_x(2.0)
       assert isinstance(r, float)
       assert r == approx(2.0)

       r = Segment(Vec2(10, 0), Vec2(0, 10)).intersection_with_axis_x(4.0)
       assert isinstance(r, float)
       assert r == approx(6.0)

       r = Segment(Vec2(0, 0), Vec2(10, 0)).intersection_with_axis_x(0)
       assert r is Segment

class TestTransform:

    def test_mat_multiply(self):
        assert Transform(-1, 2, 0, 3, -4, 5, -2, 0, 1).mul(Transform(2, -3, 1, 0, 4, -2, -1, 0, 3)) == Transform(-2, 11, -5, 1, -25, 26, -5, 6, 1)
        assert Transform(1, 2, 3, 4, 5, 6, 7, 8, 9).mul(Transform.identity()) == Transform(1, 2, 3, 4, 5, 6, 7, 8, 9)

    def test_fold_transform(self):
        assert Transform.fold_transform(Vec2(0, 1), Vec2(1, 0)).apply_to(Vec2(0, 0)) == approx(Vec2(1, 1), abs=1e-8)
        assert Transform.fold_transform(Vec2(1, 0), Vec2(0, 3**0.5)).apply_to(Vec2(0, 0)) == approx(Vec2(1.5, 0.5*3**0.5), abs=1e-8)

        t = Transform.fold_transform(Vec2(10, 0), Vec2(10, 1))
        t = t.then(t)
        for v in (Vec2(1, 1), Vec2(10, 0), Vec2(-5, -7), Vec2(20, -9)):
            assert t.apply_to(v) == approx(v, abs=1e-8)

    def test_multi_transform(self):
        t1 = Transform.translation(1, 0)
        t2 = Transform.fold_transform(Vec2(10, 0), Vec2(0, 10))
        t = t1.then(t2)
        assert t.apply_to(Vec2(1, 1)) == approx(Vec2(9, 8), abs=1e-8)
