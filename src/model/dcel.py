from dataclasses import dataclass, field

from model.geometry import Vec2
from .geometry import *

__all__ = (
    'VertexId', 'EdgeId', 'HalfEdgeId', 'FaceId',
    'Vertex', 'Edge', 'HalfEdge', 'Face',
    'DCEL'
)

class IdBase(int):

    def __eq__(self, other) -> bool:
        return type(self) is type(other) and int(self) == int(other)

    def __hash__(self) -> int:
        return hash((type(self), int(self)))

class VertexId(IdBase): pass
class EdgeId(IdBase): pass
class HalfEdgeId(IdBase): pass
class FaceId(IdBase): pass

@dataclass
class Vertex:

    pos: Vec2
    half_edge: HalfEdgeId

@dataclass
class Edge:

    half_edge0: HalfEdgeId

@dataclass
class HalfEdge:

    origin: VertexId

    edge: EdgeId
    twin: HalfEdgeId
    next: HalfEdgeId
    prev: HalfEdgeId

    face: FaceId

@dataclass
class Face:

    edge0: HalfEdgeId

@dataclass
class DCEL[V, E, F]:

    vertices: dict[VertexId, Vertex] = field(default_factory=dict)
    edges: dict[EdgeId, Edge] = field(default_factory=dict)
    half_edges: dict[HalfEdgeId, HalfEdge] = field(default_factory=dict)
    # face0 is the infinite face.
    faces: dict[FaceId, Face] = field(default_factory=dict)

    vertex_data: dict[VertexId, V] = field(default_factory=dict)
    edge_data: dict[EdgeId, E] = field(default_factory=dict)
    face_data: dict[FaceId, F] = field(default_factory=dict)

    def all_vertices_with_data(self):
        for id, v in self.vertices.items():
            yield id, v.pos, self.vertex_data[id]

    def all_edges_with_data(self):
        for id, edge in self.edges.items():
            half_edge1 = self.half_edges[edge.half_edge0]
            v1 = self.vertices[half_edge1.origin]
            half_edge2 = self.half_edges[half_edge1.twin]
            v2 = self.vertices[half_edge2.origin]
            yield id, Segment(v1.pos, v2.pos), self.edge_data[id]

    def all_faces_with_data(self):
        for id, face in self.faces.items():
            yield id, *self.query_face(id)

    def all_faces_with_data_no_infinite(self):
        for id, face in self.faces.items():
            if id == FaceId(0):
                continue
            yield id, *self.query_face(id)

    def query_face(self, face_id: FaceId) -> tuple[list[Vec2], F]:
        vertices: list[Vec2] = []
        half_edge_start = self.faces[face_id].edge0
        current_half_edge = half_edge_start
        while (current_half_edge := self.half_edges[current_half_edge].next) != half_edge_start:
            v_id = self.half_edges[current_half_edge].origin
            vertices.append(self.vertices[v_id].pos)
        return vertices, self.face_data[face_id]
