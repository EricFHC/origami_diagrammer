from typing import TypedDict, Literal
import logging
from .definition import *

logger = logging.getLogger(__file__)

class FoldFile(TypedDict):

    vertices_coords: list[list[float]]
    edges_vertices: list[list[int]]
    edges_assignment: list[Literal['M', 'B', 'V']]
    faces_vertices: list[list[int]]

def into_crease_pattern(data: FoldFile):
    logger.info("Start parsing fold file.")

    vertices: dict[VertexId, Vertex] = {
        VertexId(i): Vertex(pos=Vec2(v[0], v[1]), half_edge=HalfEdgeId(-1))
        for i, v in enumerate(data['vertices_coords'])
    }
    half_edges: dict[HalfEdgeId, HalfEdge] = {}
    edges: dict[EdgeId, Edge] = {}
    faces: dict[FaceId, Face] = {}
    edge_data: dict[EdgeId, LineType] = {}
    vertex_id_to_half_edge_id: dict[frozenset[VertexId], list[HalfEdgeId]] = {}

    logger.info("collecting all faces...")
    half_edge_cnt = 0
    for i, vs in enumerate(data['faces_vertices'], start=1):
        start = half_edge_cnt
        half_edges[HalfEdgeId(half_edge_cnt)] = HalfEdge(
            origin=VertexId(vs[0]),
            twin=HalfEdgeId(-1),
            next=HalfEdgeId(-1),
            prev=HalfEdgeId(-1),
            face=FaceId(i),
            edge=EdgeId(-1),
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
                next=HalfEdgeId(-1),
                prev=HalfEdgeId(half_edge_cnt-1),
                face=FaceId(i),
                edge=EdgeId(-1),
            )
            half_edges[HalfEdgeId(half_edge_cnt-1)].next = HalfEdgeId(half_edge_cnt)
            key = frozenset({VertexId(v1), VertexId(v2)})
            vertex_id_to_half_edge_id.setdefault(key, [])
            vertex_id_to_half_edge_id[key].append(HalfEdgeId(half_edge_cnt))
            half_edge_cnt += 1
        half_edges[HalfEdgeId(start)].prev = HalfEdgeId(half_edge_cnt-1)
        half_edges[HalfEdgeId(half_edge_cnt-1)].next= HalfEdgeId(start)
        faces[FaceId(i)] = Face(HalfEdgeId(start))

    logger.info("collecting the border...")
    borders: dict[VertexId, tuple[VertexId, HalfEdgeId, EdgeId, int]] = {} # origin and the twin of the half edge
    for i, vs in enumerate(data['edges_vertices']):
        v1 = VertexId(vs[0])
        v2 = VertexId(vs[1])
        match vertex_id_to_half_edge_id[frozenset({v1, v2})]:
            case [id1, id2]:
                half_edges[id1].twin = id2
                half_edges[id2].twin = id1
                half_edges[id1].edge = EdgeId(i)
                half_edges[id2].edge = EdgeId(i)
                edges[EdgeId(i)] = Edge(half_edge0=id1)
            case [id]:
                half_edges[id].edge = EdgeId(i)
                edges[EdgeId(i)] = Edge(half_edge0=id)
                if half_edges[id].origin == v1:
                    borders[v1] = (v2, id, EdgeId(i), len(borders))
                else:
                    borders[v2] = (v1, id, EdgeId(i), len(borders))
    for origin, (target, twin, edge, i) in borders.items():
        this_id = HalfEdgeId(half_edge_cnt+i)
        next_id = HalfEdgeId(half_edge_cnt+borders[target][3])
        half_edges[this_id] = HalfEdge(
            origin=origin,
            twin=twin,
            next=next_id,
            prev=HalfEdgeId(-1),
            face=FaceId(0),
            edge=edge,
        )
        half_edges[twin].twin = this_id
    for _, (target, _, _, i) in borders.items():
        this_id = HalfEdgeId(half_edge_cnt+i)
        next_id = HalfEdgeId(half_edge_cnt+borders[target][3])
        half_edges[next_id].prev = this_id
    faces[FaceId(0)] = Face(HalfEdgeId(half_edge_cnt+1))

    logger.info("assigning creases...")
    for i, (vs, tp) in enumerate(zip(data['edges_vertices'], data['edges_assignment'])):
        line_type = {
            'M': LineType.Mountain,
            'V': LineType.Valley,
            'B': LineType.RawEdge,
        }.get(tp, None)
        if line_type is None:
            logger.error(f"line type {tp} is not supported.")
            raise ValueError(f'Line type {tp} is yet not supported.')
        edge_data[EdgeId(i)] = line_type

    logger.info("Finish parsing.")

    return DCEL[None, LineType, None](
        vertices=vertices,
        edges=edges,
        half_edges=half_edges,
        faces=faces,
        vertex_data={i: None for i in vertices.keys()},
        edge_data=edge_data,
        face_data={i: None for i in faces.keys()},
    )