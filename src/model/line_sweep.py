from __future__ import annotations
from typing import cast, Literal
from dataclasses import dataclass, field
from .geometry import Segment, Vec2, StraightLine
from .floating import *
import bisect
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
class EventParallelWithSweepLineStart[I]:

    segment: I

@dataclass
class EventParallelWithSweepLineEnd[I]:

    segment: I

@dataclass
class EventIntersection[I]:

    segment1: I
    segment2: I

type EventNormal[I] = EventNew[I] | EventEnd[I] | EventIntersection[I]
type EventParallel[I] = EventParallelWithSweepLineStart[I] | EventParallelWithSweepLineEnd[I]
type Event[I] = EventNormal[I] | EventParallel[I]

# TODO: I hope there is a pythonic approach to rust style enum.

@dataclass
class EventAtXY[I]:

    @dataclass
    class Normal[I_]:

        event_new: list[EventNew[I_]] = field(default_factory=list)
        event_end: list[EventEnd[I_]] = field(default_factory=list)
        event_intersection: set[I_] = field(default_factory=set)

        def add_event(self, event: EventNormal[I_]):
            if isinstance(event, EventNew):
                self.event_new.append(event)
            elif isinstance(event, EventEnd):
                self.event_end.append(event)
            elif isinstance(event, EventIntersection):
                self.event_intersection.add(event.segment1)
                self.event_intersection.add(event.segment2)
            else:
                raise ValueError()

    @dataclass
    class Parallel[I_]:

        tp: Literal['start', 'end']
        segments: list[I_] = field(default_factory=list)

        def add_event(self, event: EventParallel[I_]):
            self.segments.append(event.segment)

    inner: EventAtXY.Normal[I] | EventAtXY.Parallel[I] | None = None

    def add_event(self, event: Event[I]):
        if self.inner is None:
            if isinstance(event, (EventNew, EventEnd, EventIntersection)):
                self.inner = EventAtXY.Normal()
                self.inner.add_event(event)
            elif isinstance(event, (EventParallelWithSweepLineStart, EventParallelWithSweepLineEnd)):
                self.inner = EventAtXY.Parallel('start' if isinstance(event, EventParallelWithSweepLineStart) else 'end')
                self.inner.add_event(event)
            else:
                raise ValueError()
        elif isinstance(event, (EventNew, EventEnd, EventIntersection)) and isinstance(self.inner, EventAtXY.Normal):
            self.inner.add_event(event)
        elif isinstance(event, (EventParallelWithSweepLineStart, EventParallelWithSweepLineEnd)) and isinstance(self.inner, EventAtXY.Parallel):
            self.inner.add_event(event)
        else:
            raise ValueError()

#######################################################################################################################
# AVL-Tree implement specialized for the events
#######################################################################################################################

@dataclass
class AVLNode[I]:

    y: float # Primary
    x: float # Secondary

    event: EventAtXY[I] = field(default_factory=lambda: EventAtXY())

    left: AVLNode | None = None
    right: AVLNode | None = None
    height: int = 1

    def compare_with(self, y: float, x: float, eps: float) -> Literal['l', 'g', 'e']:
        if abs(self.y - y) < eps:
            if abs(self.x - x) < eps:
                return 'e'
            elif self.x < x + eps:
                return 'l'
            else:
                return 'g'
        elif self.y < y + eps:
            return 'l'
        else:
            return 'g'

def _height(node: AVLNode | None) -> int:
    return 0 if node is None else node.height

def _update_height(node: AVLNode):
    node.height = 1 + max( _height(node.left), _height(node.right))

def _balance_factor(node: AVLNode | None) -> int:
    if node is None:
        return 0
    return _height(node.left) - _height(node.right)

def _rotate_right(s: AVLNode):
    # Illustration:
    # Before:    | After:
    #      |     |     |
    #      s     |     e
    #     / \    |    / \
    #    e   s~  |   ~e  s
    #   / \      |      / \
    #  ~e  e~s   |    e~s  s~
    e = s.left
    assert e is not None
    t = e.right

    e.right = s
    s.left = t

    _update_height(e)
    _update_height(s)

    return e

def _rotate_left(e: AVLNode):
    # The illustration is just the reverse of the one in `rotate_right`.
    s = e.right
    assert s is not None
    t = s.left

    s.left = e
    e.right = t

    _update_height(s)
    _update_height(e)

    return s

def _rotate(node: AVLNode | None) -> AVLNode | None:
    balance_factor = _balance_factor(node)
    if balance_factor > 1:
        node = cast(AVLNode, node)
        if _balance_factor(node.left) >= 0:
            return _rotate_right(node)
        node.left = _rotate_left(node.left) # type: ignore
        return _rotate_right(node)
    elif balance_factor < -1:
        node = cast(AVLNode, node)
        if _balance_factor(node.right) <= 0:
            return _rotate_left(node)
        node.right = _rotate_right(node.right) # type: ignore
        return _rotate_left(node)
    return node

def _insert(node: AVLNode | None, y: float, x: float, event: Event, eps: float):
    if node is None:
        new_node = AVLNode(y, x)
        new_node.event.add_event(event)
        return new_node
    c = node.compare_with(y, x, eps)
    if c == 'e':
        node.event.add_event(event)
        return node
    elif c == 'g':
        node.left = _insert(node.left, y, x, event, eps)
    else:
        node.right = _insert(node.right, y, x, event, eps)

    _update_height(node)

    return _rotate(node)

# Return the minimal node and the new node. This is a simple variant of the `remove operation.
def _pop_min(node: AVLNode) -> tuple[AVLNode, AVLNode | None]:
    if node.left is not None:
        minimal, node.left = _pop_min(node.left)
        _update_height(node)
        return (minimal, _rotate(node))
    else:
        if node.right is None:
            return (node, None)
        return (node, node.right)

class AVLTree[I]:

    def __init__(self):
        self._root: AVLNode[I] | None = None

    def insert(self, y: float, x: float, event: Event[I], eps: float):
        self._root = _insert(self._root, y, x, event, eps)

    def pop_min(self) -> AVLNode[I] | None:
        if self._root is None:
            return None
        node, new_root = _pop_min(self._root)
        self._root = new_root
        return node

#######################################################################################################################
# The body part of the line sweep
#######################################################################################################################

# NOTE: There should not be inf/-inf in the coords of segments inputted.
def calc_all_intersections[I](segments: dict[I, Segment], eps: float = 1e-7) -> tuple[dict[frozenset[I], Vec2], FloatSeqDict[StraightLine, set[I]]]:
    """_summary_

    Args:
        segments (dict[I, Segment]): _description_
        eps (float, optional): Epsilon for float comparison. Defaults to 1e-7.

    Returns:
        dict[frozenset[I], Vec2]: _description_
    """
    if len(segments) < 2:
        return ({}, FloatSeqDict(eps))

    events = AVLTree[I]()
    for i, s in segments.items():
        if abs(s.a.y - s.b.y) < eps:
            events.insert(s.a.y, float('-inf'), EventParallelWithSweepLineStart(i), eps)
            events.insert(s.a.y, float('+inf'), EventParallelWithSweepLineEnd(i), eps)
        elif s.a.y < s.b.y:
            events.insert(s.a.y, s.a.x, EventNew(i), eps)
            events.insert(s.b.y, s.b.x, EventEnd(i), eps)
        else:
            events.insert(s.b.y, s.b.x, EventNew(i), eps)
            events.insert(s.a.y, s.a.x, EventEnd(i), eps)

    sweep_status: list[I] = []
    checked_intersections: set[frozenset[I]] = set()
    intersections: dict[frozenset[I], Vec2] = {}
    duplicated_segments = FloatSeqDict[StraightLine, set[I]](eps)
    # TODO: Think of a name.
    # For handling segments parallel with the sweep line.
    segments_active: list[I] = [] # This follows the operations on sweep_status, except the removing operation.
    parallel_ss: list[I] = []
    flag_with_parallel: bool = False

    def check_segments(i: int, j: int):
        nonlocal sweep_status, segments, checked_intersections, duplicated_segments
        s_i = sweep_status[i]
        s_j = sweep_status[j]
        # TODO: Handle other situations.
        if frozenset({s_i, s_j}) not in checked_intersections:
            p = segments[s_i].intersection(segments[s_j])
            if isinstance(p, Vec2):
                checked_intersections.add(frozenset({s_i, s_j}))
                events.insert(p.y, p.x, EventIntersection(s_i, s_j), eps)
            elif p is Segment:
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

    while (node := events.pop_min()) is not None:
        if isinstance(node.event.inner, EventAtXY.Normal):
            # TODO: Check the order.
            for event_new in node.event.inner.event_new:
                i = event_new.segment
                y = node.y
                i_x = node.x
                index = bisect.bisect(sweep_status, i_x, key=lambda s: segments[s].intersection_with_axis_x_unsafe(y))
                sweep_status.insert(index, i)
                check_neighbor_segments(index)

                if flag_with_parallel:
                    segments_active.append(i)
            if (event_intersection := node.event.inner.event_intersection):
                # Add intersections here so that segments meeting at the same points are automatically grouped.
                intersections[frozenset(event_intersection)] = Vec2(node.x, node.y)
                for pair in combinations(event_intersection, 2):
                    checked_intersections.add(frozenset(pair))
                # Maintain the order of sweep_status.
                indices = sorted(map(sweep_status.index, node.event.inner.event_intersection))
                ss = list(map(sweep_status.__getitem__, indices))
                for i, s in zip(indices, reversed(ss)):
                    sweep_status[i] = s
                # Check new possible intersections.
                check_neighbor_segments(indices[0])
                check_neighbor_segments(indices[-1])
            for e in node.event.inner.event_end:
                s_i = e.segment
                n = len(sweep_status)
                index = sweep_status.index(s_i)
                if (i := index-1) >= 0 and (j := index+1) < n:
                    check_segments(i, j)
                del sweep_status[index]
        elif isinstance(node.event.inner, EventAtXY.Parallel):
            if node.event.inner.tp == 'start':
                parallel_ss.extend((node.event.inner.segments))
                segments_active.extend(sweep_status)
                flag_with_parallel = True
            else:
                for s_i in segments_active:
                    for s_j in parallel_ss:
                        p = segments[s_i].intersection(segments[s_j])
                        if isinstance(p, Vec2):
                            intersections[frozenset({s_i, s_j})] = p
                # Intersections between the parallel segments.
                if len(parallel_ss) > 1:
                    straight_line = StraightLine.from_segment(segments[parallel_ss[0]], eps)
                    if straight_line is not None:
                        duplicated_segments.setdefault(straight_line, set())
                        duplicated_segments[straight_line].update(parallel_ss)
                # Exit.
                flag_with_parallel = False
                parallel_ss.clear()
                segments_active.clear()

    return (intersections, duplicated_segments)
