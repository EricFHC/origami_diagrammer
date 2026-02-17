from dataclasses import dataclass, field
from enum import IntFlag, auto
from ..geometry import *
from ..dcel import *

class LineType(IntFlag):

    RawEdge = auto()
    Mountain = auto()
    Valley = auto()
    Unfolded = auto()
    Unknown = auto()
    Crease = Mountain | Valley | Unfolded | Unknown

type CreasePattern = DCEL[None, LineType, None]

@dataclass
class State:

    crease_pattern: CreasePattern = field(default_factory=DCEL)

    base_face: FaceId | None = None
    face_transforms: dict[FaceId, Transform] = field(default_factory=dict)

    cell_adjacency_graph: DCEL[None, None, list[FaceId]] = field(default_factory=DCEL)