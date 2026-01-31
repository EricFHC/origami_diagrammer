from dataclasses import dataclass, field
from typing import TypedDict, Literal, cast
from enum import IntFlag, auto
import json
from .geometry import *

class FoldFormat(TypedDict):

    vertices_coords: list[list[float]]
    edges_vertices: list[list[int]]
    edges_assignment: list[Literal['M', 'B', 'V']]
    faces_vertices: list[list[int]]

class VertexId(int): pass
class HalfEdgeId(int): pass
class LineId(int): pass
class FaceId(int): pass

@dataclass
class Vertex:

    pos: Vec2
    half_edge: HalfEdgeId

@dataclass
class HalfEdge:

    origin: VertexId
    twin: HalfEdgeId
    next_: HalfEdgeId
    prev: HalfEdgeId
    face: FaceId
    line: LineId

class LineType(IntFlag):

    RawEdge = auto()
    Mountain = auto()
    Valley = auto()
    Crease = Mountain | Valley

@dataclass
class Line:

    v1: VertexId
    v2: VertexId

    line_type: LineType

@dataclass
class Face:

    edge0: HalfEdgeId

@dataclass
class State:

    vertices: dict[VertexId, Vertex] = field(default_factory=dict)
    half_edges: dict[HalfEdgeId, HalfEdge] = field(default_factory=dict)
    lines: dict[LineId, Line] = field(default_factory=dict)
    # face0 is the infinite face.
    faces: dict[FaceId, Face] = field(default_factory=dict)

    base_face: FaceId | None = None
    face_transforms: dict[FaceId, Transform] = field(default_factory=dict)

    @staticmethod
    def load_from_fold_file(path: str):
        with open(path) as file:
            data = cast(FoldFormat, json.load(file))

        vertices: dict[VertexId, Vertex] = {
            VertexId(i): Vertex(pos=Vec2(v[0], v[1]), half_edge=HalfEdgeId(-1))
            for i, v in enumerate(data['vertices_coords'])
        }
        half_edges: dict[HalfEdgeId, HalfEdge] = {}
        lines: dict[LineId, Line] = {}
        faces: dict[FaceId, Face] = {}
        vertex_id_to_half_edge_id: dict[frozenset[VertexId], list[HalfEdgeId]] = {}

        half_edge_cnt = 0
        for i, vs in enumerate(data['faces_vertices']):
            start = half_edge_cnt
            half_edges[HalfEdgeId(half_edge_cnt)] = HalfEdge(
                origin=VertexId(vs[0]),
                twin=HalfEdgeId(-1),
                next_=HalfEdgeId(-1),
                prev=HalfEdgeId(-1),
                face=FaceId(i+1),
                line=LineId(-1),
            )
            vertices[VertexId(vs[0])].half_edge = HalfEdgeId(half_edge_cnt)
            key = frozenset({VertexId(vs[0]), VertexId(vs[1])})
            vertex_id_to_half_edge_id.setdefault(key, [])
            vertex_id_to_half_edge_id[key].append(HalfEdgeId(half_edge_cnt))
            half_edge_cnt += 1
            for v1, v2 in zip(vs[1:], vs[2:]+vs[0:1]):
                half_edges[HalfEdgeId(half_edge_cnt)] = HalfEdge(
                    origin=VertexId(v1),
                    twin=HalfEdgeId(-1),
                    next_=HalfEdgeId(-1),
                    prev=HalfEdgeId(half_edge_cnt-1),
                    face=FaceId(i),
                    line=LineId(-1),
                )
                half_edges[HalfEdgeId(half_edge_cnt-1)].next_ = HalfEdgeId(half_edge_cnt)
                key = frozenset({VertexId(v1), VertexId(v2)})
                vertex_id_to_half_edge_id.setdefault(key, [])
                vertex_id_to_half_edge_id[key].append(HalfEdgeId(half_edge_cnt))
                half_edge_cnt += 1
            half_edges[HalfEdgeId(start)].prev = HalfEdgeId(half_edge_cnt-1)
            half_edges[HalfEdgeId(half_edge_cnt-1)].next_ = HalfEdgeId(start)
            faces[FaceId(i+1)] = Face(HalfEdgeId(start))

        borders: dict[VertexId, tuple[VertexId, HalfEdgeId, LineId, int]] = {} # origin and the twin of the half edge
        for i, vs in enumerate(data['edges_vertices']):
            v1 = VertexId(vs[0])
            v2 = VertexId(vs[1])
            match vertex_id_to_half_edge_id[frozenset({v1, v2})]:
                case [id1, id2]:
                    half_edges[id1].twin = id2
                    half_edges[id2].twin = id1
                    half_edges[id1].line = LineId(i)
                    half_edges[id2].line = LineId(i)
                case [id]:
                    half_edges[id].line = LineId(i)
                    if half_edges[id].origin == v1:
                        borders[v1] = (v2, id, LineId(i), len(borders))
                    else:
                        borders[v2] = (v1, id, LineId(i), len(borders))
        for origin, (target, twin, line, i) in borders.items():
            this_id = HalfEdgeId(half_edge_cnt+i)
            next_id = HalfEdgeId(half_edge_cnt+borders[target][3])
            half_edges[this_id] = HalfEdge(
                origin=origin,
                twin=twin,
                next_=next_id,
                prev=HalfEdgeId(-1),
                face=FaceId(0),
                line=line,
            )
            half_edges[twin].twin = this_id
        for _, (target, _, _, i) in borders.items():
            this_id = HalfEdgeId(half_edge_cnt+i)
            next_id = HalfEdgeId(half_edge_cnt+borders[target][3])
            half_edges[next_id].prev = this_id
        faces[FaceId(0)] = Face(HalfEdgeId(half_edge_cnt+1))

        for i, (vs, tp) in enumerate(zip(data['edges_vertices'], data['edges_assignment'])):
            v1 = VertexId(vs[0])
            v2 = VertexId(vs[1])
            line_type = {
                'M': LineType.Mountain,
                'V': LineType.Valley,
                'B': LineType.RawEdge,
            }.get(tp, None)
            if line_type is None:
                raise ValueError(f'Line type {tp} is yet not supported.')
            lines[LineId(i)] = Line(v1=v1, v2=v2, line_type=line_type)

        return State(
            vertices=vertices,
            half_edges=half_edges,
            lines=lines,
            faces=faces,
            base_face=FaceId(1),
        )

    def _calc_face_transform(self):
        # Use DFS search.
        def search(target: FaceId, target_transform: Transform):
            self.face_transforms[target] = target_transform
            start = self.faces[target].edge0
            edge = start
            while (edge := self.half_edges[edge].next_) != start:
                neighbor_face_edge = self.half_edges[edge].twin
                neighbor_face = self.half_edges[neighbor_face_edge].face
                if not neighbor_face in self.face_transforms:
                    p1 = self.vertices[self.half_edges[edge].origin].pos
                    p2 = self.vertices[self.half_edges[self.half_edges[edge].next_].origin].pos
                    search(neighbor_face, target_transform.then(Transform.fold_transform(p1, p2)))
        if self.base_face is None:
            raise ValueError('The base face is yet not assigned.')
        search(self.base_face, Transform.identity())

    def draw_object_points(self):
        yield from {id: v.pos for id, v in self.vertices.items()}.items()

    def draw_object_lines(self):
        for i, l in self.lines.items():
            yield i, self.vertices[l.v1].pos, self.vertices[l.v2].pos, l.line_type

    def draw_object_face(self):
        for i, f in self.faces.items():
            start = f.edge0
            edge = start
            coord: list[float] = []
            while (edge := self.half_edges[edge].next_) != start:
                pos = self.vertices[self.half_edges[edge].origin].pos
                coord.append(pos.x)
                coord.append(pos.y)
            yield i, coord