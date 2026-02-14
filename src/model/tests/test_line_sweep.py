from model.geometry import *
from model.line_sweep import *
from model.floating import *
from math import pi, sqrt
from pytest import approx

class TestLineSweep:

    # NOTE: Cannot use `assert results == approx(expected)`, in which case `__eq__` will be called, instead of desired
    # things like `math.isclose`.
    def assert_res(self, results, expected):
        for k in results.keys():
            assert k in expected
        for k, v in expected.items():
            assert k in results
            assert tuple(results[k]) == approx(tuple(v), abs=1e-8)

    def display_res(self, results, expected):
        all_key = set(tuple(results.keys()) + tuple(expected.keys()))
        r_only = []
        e_only = []
        print('---common: re, ex---')
        for key in all_key:
            if (key in results) and (key in expected):
                r = results[key]
                e = expected[key]
                print(key, r, e, "ok" if tuple(r) == approx(tuple(e), abs=1e-8) else "err")
            elif key in results:
                r_only.append(key)
            else:
                e_only.append(key)
        print('--result spec--')
        for key in r_only:
            print(key, results[key])
        print('--expected spec--')
        for key in e_only:
            print(key, expected[key])

    def test_trival(self):
        segments = dict(enumerate((
           Segment(Vec2(15, 17),Vec2(7, 3)),
           Segment(Vec2(3, 16), Vec2(6, 10)),
           Segment(Vec2(2, 15), Vec2(12, 8)),
           Segment(Vec2(7, 14), Vec2(11, 6)),
           Segment(Vec2(10, 13),Vec2(2, 4)),
           Segment(Vec2(1, 12), Vec2(9, 5)),
           Segment(Vec2(-1, 11),Vec2(5, 2)),
        )))
        expected = {
            frozenset({0, 2}): Vec2(10.469387755, 9.071428571),
            frozenset({0, 3}): Vec2(9.933333333, 8.133333333),
            frozenset({0, 5}): Vec2(8.428571429, 5.5),
            frozenset({1, 2}): Vec2(4.307692308, 13.384615385),
            frozenset({2, 3}): Vec2(8.923076923, 10.153846154),
            frozenset({2, 4}): Vec2(8.027397260, 10.780821918),
            frozenset({3, 4}): Vec2(8.4, 11.2),
            frozenset({4, 5}): Vec2(5.5625, 8.0078125),
            frozenset({4, 6}): Vec2(2.952380952, 5.071428571),
        }
        results, dup = calc_all_intersections(segments)
        assert len(dup) == 0
        self.assert_res(results, expected)

    def test_trival2(self):
        segments = dict(enumerate((
            Segment(Vec2(0, 0), Vec2(4, 4)),
            Segment(Vec2(1, 0), Vec2(5, 4)),
            Segment(Vec2(2, 0), Vec2(2, 10)),
            Segment(Vec2(3, 0), Vec2(3, 10)),
            Segment(Vec2(1, 6), Vec2(6, 1)),
        )))
        expected = {
            frozenset({2, 1}): Vec2(2, 1),
            frozenset({2, 0}): Vec2(2, 2),
            frozenset({2, 4}): Vec2(2, 5),
            frozenset({3, 1}): Vec2(3, 2),

            frozenset({3, 0}): Vec2(3, 3),
            frozenset({3, 4}): Vec2(3, 4),
            frozenset({0, 4}): Vec2(3.5, 3.5),

            frozenset({1, 4}): Vec2(4, 3),
        }
        results, dup = calc_all_intersections(segments)
        assert len(dup) == 0
        self.display_res(results, expected)
        self.assert_res(results, expected)

    def test_multi_events_at_a_time(self):
        segments = dict(enumerate((
            Segment(Vec2(1, 1), Vec2(5, 5)),
            Segment(Vec2(2, 7), Vec2(7, 2)),
            Segment(Vec2(3, 0), Vec2(3, 8)),
            Segment(Vec2(1, 6), Vec2(4, 3)),
            Segment(Vec2(5, 1), Vec2(8, 4)),
            Segment(Vec2(8, 2), Vec2(8, 7)),
            Segment(Vec2(0, 8), Vec2(3, 5)),
        )))
        expected = {
            frozenset({0, 2}): Vec2(3, 3),
            frozenset({2, 3}): Vec2(3, 4),
            frozenset({2, 6}): Vec2(3, 5),
            frozenset({1, 2}): Vec2(3, 6),
            frozenset({0, 3}): Vec2(3.5, 3.5),
            frozenset({0, 1}): Vec2(4.5, 4.5),
            frozenset({1, 4}): Vec2(6.5, 2.5),
            frozenset({4, 5}): Vec2(8, 4),
        }
        results, dup = calc_all_intersections(segments)
        assert len(dup) == 0
        self.assert_res(results, expected)

    def test_segment_parallel_with_sweep_line(self):
        segments = dict(enumerate((
            Segment(Vec2(1, 1), Vec2(5, 5)),
            Segment(Vec2(2, 7), Vec2(7, 2)),
            Segment(Vec2(3, 0), Vec2(3, 8)),
            Segment(Vec2(1, 6), Vec2(4, 3)),
            Segment(Vec2(5, 1), Vec2(8, 4)),
            Segment(Vec2(8, 2), Vec2(8, 7)),
            Segment(Vec2(0, 8), Vec2(3, 5)),

            Segment(Vec2(2, 2), Vec2(6, 2)),
            Segment(Vec2(7, 7), Vec2(8, 7)),
        )))
        expected = {
            frozenset({0, 2}): Vec2(3, 3),
            frozenset({2, 3}): Vec2(3, 4),
            frozenset({2, 6}): Vec2(3, 5),
            frozenset({1, 2}): Vec2(3, 6),
            frozenset({0, 3}): Vec2(3.5, 3.5),
            frozenset({0, 1}): Vec2(4.5, 4.5),
            frozenset({1, 4}): Vec2(6.5, 2.5),
            frozenset({4, 5}): Vec2(8, 4),

            frozenset({0, 7}): Vec2(2, 2),
            frozenset({4, 7}): Vec2(6, 2),
            frozenset({2, 7}): Vec2(3, 2),
            frozenset({5, 8}): Vec2(8, 7),
        }
        results, dup = calc_all_intersections(segments)
        assert len(dup) == 0
        self.display_res(results, expected)
        self.assert_res(results, expected)

    def test_segment_parallel_with_sweep_line2(self):
        segments = dict(enumerate((
            Segment(Vec2(1, 0), Vec2(1, 3)),
            Segment(Vec2(2, 0), Vec2(2, 3)),

            Segment(Vec2(0, 1), Vec2(3, 1)),
            Segment(Vec2(0, 2), Vec2(3, 2)),
        )))
        expected = {
            frozenset({0, 2}): Vec2(1, 1),
            frozenset({0, 3}): Vec2(1, 2),
            frozenset({1, 2}): Vec2(2, 1),
            frozenset({1, 3}): Vec2(2, 2),
        }
        results, dup = calc_all_intersections(segments)
        assert len(dup) == 0
        self.display_res(results, expected)
        self.assert_res(results, expected)

    def test_multi_segments_at_a_point(self):
        segments = dict(enumerate((
            Segment(Vec2(0, 0), Vec2(4, 4)),
            Segment(Vec2(1, 0), Vec2(5, 4)),
            Segment(Vec2(2, 0), Vec2(2, 10)),
            Segment(Vec2(3, 0), Vec2(3, 10)),
            Segment(Vec2(1, 5), Vec2(5, 1)),
        )))
        expected = {
            frozenset({2, 1}): Vec2(2, 1),
            frozenset({2, 0}): Vec2(2, 2),
            frozenset({2, 4}): Vec2(2, 4),
            frozenset({3, 1}): Vec2(3, 2),

            frozenset({3, 0, 4}): Vec2(3, 3),

            frozenset({1, 4}): Vec2(3.5, 2.5),
        }
        results, dup = calc_all_intersections(segments)
        assert len(dup) == 0
        self.display_res(results, expected)
        self.assert_res(results, expected)

    def test_multi_segments_at_a_point2(self):
        segments = dict(enumerate((
            Segment(Vec2(0, 8), Vec2(8, 0)),

            Segment(Vec2(0, 16/3), Vec2(5, 7)),
            Segment(Vec2(0, 4), Vec2(4, 8)),
            Segment(Vec2(1, 3), Vec2(8/3, 8)),

            Segment(Vec2(-1, 5), Vec2(8, 2)),
            Segment(Vec2(3, 9), Vec2(6, 0)),
        )))
        expected = {
            frozenset({0, 1, 2, 3}): Vec2(2, 6),
            frozenset({0, 4, 5}): Vec2(5, 3),

            frozenset({2, 4}): Vec2(0.5, 4.5),
            frozenset({3, 4}): Vec2(1.4, 4.2),

            frozenset({1, 5}): Vec2(3.8, 6.6),
            frozenset({2, 5}): Vec2(3.5, 7.5),
        }
        results, dup = calc_all_intersections(segments)
        assert len(dup) == 0
        self.display_res(results, expected)
        self.assert_res(results, expected)

    def test_duplicated_segments(self):
        segments = dict(enumerate((
            Segment(Vec2(0, 0), Vec2(2, 2)),
            Segment(Vec2(1, 1), Vec2(3, 3)),
            Segment(Vec2(0, 3), Vec2(3, 0)),

            Segment(Vec2(0, 1), Vec2(3, 1)),

            Segment(Vec2(1, 1), Vec2(2, 2)),
        )))
        expected = {
            frozenset({1, 2, 0, 4}): Vec2(1.5, 1.5),

            frozenset({3, 0}): Vec2(1, 1),
            frozenset({3, 2}): Vec2(2, 1),
            frozenset({3, 1}): Vec2(1, 1),
            frozenset({3, 4}): Vec2(1, 1),
        }
        expected_dup = FloatSeqDict.from_pair(
            1e-8,
            (StraightLine(-pi/4, 0.0), {0, 1, 4}),
        )
        results, dup = calc_all_intersections(segments)

        self.display_res(results, expected)
        self.assert_res(results, expected)

        self.display_res(dup, expected_dup)
        self.assert_res(dup, expected_dup)

    def test_duplicated_segments_with_parallel(self):
        segments = dict(enumerate((
            Segment(Vec2(0, 0), Vec2(2, 2)),
            Segment(Vec2(1, 1), Vec2(3, 3)),
            Segment(Vec2(0, 3), Vec2(3, 0)),

            Segment(Vec2(0, 1), Vec2(3, 1)),

            Segment(Vec2(1, 0), Vec2(4, 3)),
            Segment(Vec2(2, 1), Vec2(4, 3)),
        )))
        expected = {
            frozenset({1, 2, 0}): Vec2(1.5, 1.5),
            frozenset({4, 5, 2, 3}): Vec2(2, 1),

            frozenset({3, 0, 1}): Vec2(1, 1),
        }
        expected_dup = FloatSeqDict.from_pair(
            1e-8,
            (StraightLine(-pi/4, 0.0), {0, 1}),
            (StraightLine(-pi/4, sqrt(2)/2), {4, 5}),
        )
        results, dup = calc_all_intersections(segments)

        self.display_res(results, expected)
        self.assert_res(results, expected)

        self.display_res(dup, expected_dup)
        self.assert_res(dup, expected_dup)