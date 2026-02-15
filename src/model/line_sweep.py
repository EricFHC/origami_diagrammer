from __future__ import annotations
from typing import cast, Literal
from dataclasses import dataclass, field
from .geometry import Segment, Vec2, StraightLine
from .floating import *
import bisect
from math import pi
from itertools import combinations

__all__ = ('calc_all_intersections', )

# Some overall notes.
# The sweep line is parallel with the x axis, with its y increasing.

#######################################################################################################################
# Events
#######################################################################################################################

@dataclass
class EventNew[I]:

    segment: I

@dataclass
class EventEnd[I]:

    segment: I

@dataclass
class EventIntersection[I]:

    segment1: I
    segment2: I

type EventNormal[I] = EventNew[I] | EventEnd[I] | EventIntersection[I]

@dataclass
class EventAtXY[I]:

    new: list[I]= field(default_factory=list)
    end: list[I] = field(default_factory=list)
    intersection: set[I] = field(default_factory=set)

    def add_event(self, event: EventNormal[I]):
        match event:
            case EventNew(s):
                self.new.append(s)
            case EventEnd(s):
                self.end.append(s)
            case EventIntersection(s_i, s_j):
                self.intersection.update((s_i, s_j))
            case _:
                raise RuntimeError()

@dataclass
class EventAtY[I]:

    normal_events: FloatSeqDict[tuple[float], EventAtXY[I]]
    parallel: list[I] = field(default_factory=list)

    def add_event(self, x: float, event: EventNormal[I]):
        self.normal_events.setdefault((x, ), EventAtXY())
        self.normal_events[(x, )].add_event(event)

    def add_parallel(self, s: I):
        self.parallel.append(s)

@dataclass
class Events[I]:

    eps: float
    inner: FloatSeqDict[tuple[float], EventAtY[I]] = field(init=False)

    def __post_init__(self):
        self.inner = FloatSeqDict(self.eps)

    def add_event(self, y: float, x: float, event: EventNormal[I]):
        self.inner.setdefault((y, ), EventAtY(FloatSeqDict(self.eps)))
        self.inner[(y, )].add_event(x, event)

    def add_parallel(self, y: float, s: I):
        self.inner.setdefault((y, ), EventAtY(FloatSeqDict(self.eps)))
        self.inner[(y, )].add_parallel(s)

    def pop_min(self) -> tuple[float, EventAtY[I]] | None:
        res = self.inner.pop_min()
        if res is None:
            return None
        k, v = res
        return (k[0], v)

#######################################################################################################################
# The body part of the line sweep
#######################################################################################################################

def calc_all_intersections[I](segments: dict[I, Segment], eps: float = 1e-7) -> tuple[dict[frozenset[I], Vec2], FloatSeqDict[StraightLine, set[I]]]:
    """Calculate all the intersection points of the given segments and by the way collect duplicated segments.

    - intersection: The intersection of two segments is a point.
    - duplication: The intersection of two segments is a segment.

    Note:
        - Duplicated segments are not strictly collected. As long as two segments is detected duplicated, they are added
        to a straight-line group. Thus, segments in a straight-line group may not all duplicate each other in pairs.
        - For segments parallel with the sweep-line, segments with the same y are all grouped without further detection
        unless there is only one segment.

    Args:
        segments (dict[I, Segment]): Segments. I for identifier.
        eps (float, optional): Epsilon for float comparison. Defaults to 1e-7.

    Returns:
        _todo_
    """
    if len(segments) < 2:
        return ({}, FloatSeqDict(eps))

    events: Events[I] = Events(eps)
    for i, s in segments.items():
        if abs(s.a.y - s.b.y) < eps:
            events.add_parallel(s.a.y, i)
        elif s.a.y < s.b.y:
            events.add_event(s.a.y, s.a.x, EventNew(i))
            events.add_event(s.b.y, s.b.x, EventEnd(i))
        else:
            events.add_event(s.b.y, s.b.x, EventNew(i))
            events.add_event(s.a.y, s.a.x, EventEnd(i))

    sweep_status: list[I] = []
    checked_intersections: set[frozenset[I]] = set()
    intersections: FloatSeqDict[Vec2, set[I]] = FloatSeqDict(eps)
    duplicated_segments: FloatSeqDict[StraightLine, set[I]] = FloatSeqDict(eps)

    # For handling segments parallel with the sweep line.
    segments_active: list[I] = [] # This follows the operations on sweep_status, except the removing operation.
    flag_with_parallel: bool = False

    def check_segments(i: int, j: int):
        nonlocal sweep_status, segments, checked_intersections, duplicated_segments
        s_i = sweep_status[i]
        s_j = sweep_status[j]
        if frozenset({s_i, s_j}) not in checked_intersections:
            p = segments[s_i].intersection(segments[s_j], eps)
            checked_intersections.add(frozenset({s_i, s_j}))
            if isinstance(p, Vec2):
                events.add_event(p.y, p.x, EventIntersection(s_i, s_j))
            elif isinstance(p, Segment):
                straight_line = StraightLine.from_segment(segments[s_i], eps)
                if straight_line is None:
                    raise RuntimeError()
                duplicated_segments.setdefault(straight_line, set())
                duplicated_segments[straight_line].update({s_i, s_j})

    def check_neighbor_segments(index: int):
        nonlocal sweep_status
        n = len(sweep_status)
        if 0 <= index-1:
            check_segments(index, index-1)
        if index+1 < n:
            check_segments(index, index+1)

    while (pop_res := events.pop_min()) is not None:
        y, event_at_y = pop_res
        if event_at_y.parallel:
            flag_with_parallel = True
        else:
            flag_with_parallel = False
        segments_active.extend(sweep_status)

        for x_, event_at_xy in event_at_y.normal_events.items():
            x = x_[0]

            for i in event_at_xy.new:
                index = bisect.bisect(sweep_status, x, key=lambda s: segments[s].intersection_with_axis_x_unsafe(y, eps))
                sweep_status.insert(index, i)
                check_neighbor_segments(index)

            if flag_with_parallel:
                segments_active.extend(event_at_xy.new)

            if (intersection_at_xy := event_at_xy.intersection.copy()):
                # Record all intersections.
                intersections.setdefault(Vec2(x, y), set())
                intersections[Vec2(x, y)].update(intersection_at_xy)
                for pair in combinations(intersection_at_xy, 2):
                    checked_intersections.add(frozenset(pair))

                # Maintain the order of sweep_status.
                indices = sorted(map(sweep_status.index, event_at_xy.intersection))
                ss = list(map(sweep_status.__getitem__, indices))
                for i, s in zip(indices, reversed(ss)):
                    sweep_status[i] = s

                # Check new possible intersections.
                check_neighbor_segments(indices[0])
                check_neighbor_segments(indices[-1])

            for s_i in event_at_xy.end:
                n = len(sweep_status)
                index = sweep_status.index(s_i)
                if (i := index-1) >= 0 and (j := index+1) < n:
                    check_segments(i, j)
                del sweep_status[index]

        # Check parallel.
        if len(event_at_y.parallel) > 1:
            duplicated_segments[StraightLine(pi/2, y)] = set(event_at_y.parallel)
        for s_i in event_at_y.parallel:
            for s_j in segments_active:
                p = segments[s_i].intersection(segments[s_j], eps)
                if isinstance(p, Vec2):
                    intersections.setdefault(p, set())
                    intersections[p].update((s_i, s_j))

        segments_active.clear()

    return ({frozenset(v): k for k, v in intersections.items()}, duplicated_segments)
