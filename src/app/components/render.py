from __future__ import annotations
from widgets.canvas import CanvasSelectionControl, CanvasSelectionChild, ItemStyleOfState, ItemStyleCommon
from model.state.definition import CreasePattern, LineType, VertexId, EdgeId, FaceId
from enum import IntFlag, auto

class FoldedStateStyle(IntFlag):

    RawEdge = auto()
    Mountain = auto()
    Valley = auto()
    Crease = Mountain | Valley

    Vertex = auto()

    FaceWhite = auto()
    FaceColor= auto()
    Face = FaceColor | FaceWhite

class FoldedStateRender(CanvasSelectionControl[VertexId | EdgeId | FaceId]):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.set_style()

    def set_style(self):
        self.style[FoldedStateStyle.Vertex] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='#000000').into_dict(),
            hover=ItemStyleCommon(fill='#F39C12').into_dict(),
            selected=ItemStyleCommon(fill='#3498DB').into_dict(),
            selected_hover=ItemStyleCommon(fill='#F1C40F').into_dict(),
        )

        self.style[FoldedStateStyle.RawEdge] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='black').into_dict(),
            hover=ItemStyleCommon(dash='--').into_dict(),
            selected=ItemStyleCommon(fill='purple').into_dict(),
            selected_hover=ItemStyleCommon().into_dict(),
        ).auto_complete()
        self.style[FoldedStateStyle.Mountain] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='red').into_dict(),
            hover=ItemStyleCommon(dash='--').into_dict(),
            selected=ItemStyleCommon(fill='purple').into_dict(),
            selected_hover=ItemStyleCommon().into_dict(),
        ).auto_complete()
        self.style[FoldedStateStyle.Valley] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='blue').into_dict(),
            hover=ItemStyleCommon(dash='--').into_dict(),
            selected=ItemStyleCommon(fill='purple').into_dict(),
            selected_hover=ItemStyleCommon().into_dict(),
        ).auto_complete()

        self.style[FoldedStateStyle.FaceWhite] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='').into_dict(),
            hover=ItemStyleCommon(fill='green', stipple='gray50').into_dict(),
            selected=ItemStyleCommon().into_dict(),
            selected_hover=ItemStyleCommon().into_dict(),
        ).auto_complete()

    def load_crease_pattern(self, cp: CreasePattern):
        for i, f, _ in cp.all_faces_with_data_no_infinite():
            self.add_face(*f, style=FoldedStateStyle.FaceWhite, userdata=i)

        for i, (p1, p2), line_type in cp.all_edges_with_data():
            style = {
                LineType.Mountain: FoldedStateStyle.Mountain,
                LineType.Valley: FoldedStateStyle.Valley,
                LineType.RawEdge: FoldedStateStyle.RawEdge,
            }[line_type]
            self.add_line(p1.x, p1.y, p2.x, p2.y, style=style, userdata=i)

        for i, p, _ in cp.all_vertices_with_data():
            self.add_point(p.x, p.y, 4, style=FoldedStateStyle.Vertex, userdata=i)

class CreasePatternStyle(IntFlag):

    RawEdge = auto()
    Mountain = auto()
    Valley = auto()

    Vertex = auto()

    Face = auto()

class CreasePatternRender(CanvasSelectionChild):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.set_style()

    def set_style(self):
        self.style[CreasePatternStyle.Vertex] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='black').into_dict(),
            hover=ItemStyleCommon().into_dict(),
            selected=ItemStyleCommon().into_dict(),
            selected_hover=ItemStyleCommon().into_dict(),
        )

        self.style[CreasePatternStyle.RawEdge] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='black').into_dict(),
            hover=ItemStyleCommon(dash='--').into_dict(),
            selected=ItemStyleCommon(fill='purple').into_dict(),
            selected_hover=ItemStyleCommon().into_dict(),
        ).auto_complete()
        self.style[CreasePatternStyle.Mountain] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='red').into_dict(),
            hover=ItemStyleCommon(dash='--').into_dict(),
            selected=ItemStyleCommon(fill='purple').into_dict(),
            selected_hover=ItemStyleCommon().into_dict(),
        ).auto_complete()
        self.style[CreasePatternStyle.Valley] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='blue').into_dict(),
            hover=ItemStyleCommon(dash='--').into_dict(),
            selected=ItemStyleCommon(fill='purple').into_dict(),
            selected_hover=ItemStyleCommon().into_dict(),
        ).auto_complete()

        self.style[CreasePatternStyle.Face] = ItemStyleOfState(
            normal=ItemStyleCommon(fill='white').into_dict(),
            hover=ItemStyleCommon(fill='green', stipple='gray50').into_dict(),
            selected=ItemStyleCommon().into_dict(),
            selected_hover=ItemStyleCommon().into_dict(),
        ).auto_complete()

    def load_crease_pattern(self, cp: CreasePattern):
        for i, f, _ in cp.all_faces_with_data_no_infinite():
            self.add_face(*f, style=CreasePatternStyle.Face, userdata=i)

        for i, (p1, p2), line_type in cp.all_edges_with_data():
            style = {
                LineType.Mountain: CreasePatternStyle.Mountain,
                LineType.Valley: CreasePatternStyle.Valley,
                LineType.RawEdge: CreasePatternStyle.RawEdge,
            }[line_type]
            self.add_line(p1.x, p1.y, p2.x, p2.y, style=style, userdata=i)

        for i, p, _ in cp.all_vertices_with_data():
            self.add_point(p.x, p.y, 2, style=FoldedStateStyle.Vertex, userdata=i)

# class StateRenderCanvas(CanvasPlus):

#     def __init__(self, parent=None, **kwargs):
#         kwargs.update(closeenough=1.5)
#         super().__init__(parent, **kwargs)

#         self.anchor_current_state_unfold = Anchor(self, 100, 150, 100)
#         self.anchor_current_state_folded = Anchor(self, 100, 250, 175)
#         self.anchor_next_state_preview = Anchor(self, 500, 250, 175)

#         self._folded_id_map: dict[int, VertexId|LineId|FaceId] = {}
#         self._unfold_id_map: dict[VertexId|LineId|FaceId, int] = {}

#         self._var_newly_selected = IntVar()
#         self._hover_id: int | None = None
#         self._selected_id = set[int]()

#         self._on_configure(None)
#         self.bind('<Configure>', self._on_configure)

#     def set_state(self, state: DifferentiableRefCell[State, FrozenState, StateDifference]):
#         self._state = state
#         self._folding = None # TODO
#         self.delete('all')
#         self._folded_id_map.clear()
#         self._unfold_id_map.clear()
#         self._render_folded_state()
#         self._render_unfold_state()

#     def update_state(self, diff: StateDifference, new_state: FrozenState):
#         pass

#     def _on_configure(self, _):
#         w = self.winfo_width()
#         h = self.winfo_height()
#         self.anchor_current_state_folded.move_to(w//2, h//2)
#         self.anchor_current_state_unfold.move_to(w-120, 120)

#     def end_selection(self):
#         for i in self._selected_id:
#             self._set_folded_item_style(
#                 i,
#                 self.style_folded.get('normal')
#             )
#             self._set_unfold_item_style(
#                 self._folded_id_map[i],
#                 self.style_unfold.get('normal')
#             )
#         self._selected_id.clear()

#     def select_item_immediate(self, type_: Literal['vertex', 'line', 'face']) -> VertexId | LineId | FaceId:
#         i1 = self.tag_bind(type_, '<Enter>', self._on_enter)
#         i2 = self.tag_bind(type_, '<Leave>', self._on_leave)
#         i3 = self.tag_bind(type_, '<ButtonRelease-1>', self._on_press)
#         self.wait_variable(self._var_newly_selected)
#         self.tag_unbind(type_, '<Enter>', i1)
#         self.tag_unbind(type_, '<Leave>', i2)
#         self.tag_unbind(type_, '<ButtonRelease-1>', i3)
#         return self._folded_id_map[self._var_newly_selected.get()]

#     def _render_folded_state(self):
#         drawn_vertices = set[VertexId]()
#         drawn_lines = set[LineId]()
#         state = self._state.borrow()
#         anchor = self.anchor_current_state_folded
#         style = self.style_folded.get('normal')

#         for f_id, f in state.topological_sorting():
#             self._folded_id_map[anchor.draw_poly(
#                 *tuple(state.folded_vertices[i] for i in f.vertices),
#                 tags=('face', ),
#                 **(style.face_colored if f.side else style.face_white)
#             )] = f_id

#             for l_id in f.edges:
#                 if l_id in drawn_lines:
#                     continue
#                 drawn_lines.add(l_id)
#                 v1 = state.folded_vertices[l_id.v1]
#                 v2 = state.folded_vertices[l_id.v2]
#                 self._folded_id_map[anchor.draw_line(
#                     v1, v2,
#                     tags=('line', ),
#                     **(style.crease if state.lines[l_id] == LineType.C else style.edge)
#                 )] = l_id

#             for v_id in f.vertices:
#                 if v_id in drawn_vertices:
#                     continue
#                 drawn_vertices.add(v_id)
#                 v = state.folded_vertices[v_id]
#                 self._folded_id_map[anchor.draw_point(
#                     v, 2, tags=('vertex', ), **style.vertex
#                 )] = v_id

#     def _render_unfold_state(self):
#         state = self._state.borrow()
#         anchor = self.anchor_current_state_unfold
#         style = self.style_unfold.get('normal')
#         for f_id, f in state.faces.items():
#             self._unfold_id_map[f_id] = anchor.draw_poly(*tuple(state.folded_vertices[i] for i in f.vertices), **style.face)
#         for l_id, l in state.lines.items():
#             s = {LineType.M: style.mountain, LineType.V: style.valley, LineType.C: style.crease, LineType.R: style.raw_edge}[l]
#             self._unfold_id_map[l_id] = anchor.draw_line(state.unfold_vertices[l_id.v1], state.unfold_vertices[l_id.v2], **s)
#         for v_id, v in state.unfold_vertices.items():
#             self._unfold_id_map[v_id] = anchor.draw_point(v, 2, **style.vertex)