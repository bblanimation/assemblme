# Copyright (C) 2025 Christopher Gearhart
# christopher@bricksbroughttolife.com
# http://bricksbroughttolife.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# CODE FROM: http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Modeling/offset_edges

# System imports
import math
from math import sin, cos, pi, copysign, radians, degrees atan, sqrt
from time import perf_counter

# Blender imports
import bpy
from bpy_extras import view3d_utils
import bmesh
from mathutils import Vector

# Module imports
from .blender import *

X_UP = Vector((1.0, .0, .0))
Y_UP = Vector((.0, 1.0, .0))
Z_UP = Vector((.0, .0, 1.0))
ZERO_VEC = Vector((.0, .0, .0))
ANGLE_1 = pi / 180
ANGLE_90 = pi / 2
ANGLE_180 = pi
ANGLE_360 = 2 * pi


def is_face_selected(ob_edit):
    bpy.ops.object.mode_set(mode="OBJECT")
    me = ob_edit.data
    for p in me.polygons:
        if p.select:
            bpy.ops.object.mode_set(mode="EDIT")
            return True
    bpy.ops.object.mode_set(mode="EDIT")

    return False


def is_mirrored(ob_edit):
    for mod in ob_edit.modifiers:
        if mod.type == "MIRROR" and mod.use_mirror_merge:
            return True
    return False


def reorder_loop(verts, edges, lp_normal, adj_faces):
    for i, adj_f in enumerate(adj_faces):
        if adj_f is None:
            continue
        v1, v2 = verts[i], verts[i+1]
        e = edges[i]
        fv = tuple(adj_f.verts)
        if fv[fv.index(v1)-1] is v2:
            # Align loop direction
            verts.reverse()
            edges.reverse()
            adj_faces.reverse()
        if lp_normal.dot(adj_f.normal) < .0:
            lp_normal *= -1
        break
    else:
        # All elements in adj_faces are None
        for v in verts:
            if v.normal != ZERO_VEC:
                if lp_normal.dot(v.normal) < .0:
                    verts.reverse()
                    edges.reverse()
                    lp_normal *= -1
                break

    return verts, edges, lp_normal, adj_faces


def get_cross_rail(vec_tan, vec_edge_r, vec_edge_l, normal_r, normal_l):
    # Cross rail is a cross vector between normal_r and normal_l.

    vec_cross = normal_r.cross(normal_l)
    if vec_cross.dot(vec_tan) < .0:
        vec_cross *= -1
    cos_min = min(vec_tan.dot(vec_edge_r), vec_tan.dot(-vec_edge_l))
    cos = vec_tan.dot(vec_cross)
    if cos >= cos_min:
        vec_cross.normalize()
        return vec_cross
    else:
        return None


def get_edge_rail(vert, set_edges_orig):
    co_edges = co_edges_selected = 0
    vec_inner = None
    for e in vert.link_edges:
        if (e not in set_edges_orig and
           (e.select or (co_edges_selected == 0 and not e.hide))):
            v_other = e.other_vert(vert)
            vec = v_other.co - vert.co
            if vec != ZERO_VEC:
                vec_inner = vec
                if e.select:
                    co_edges_selected += 1
                    if co_edges_selected == 2:
                        return None
                else:
                    co_edges += 1
    if co_edges_selected == 1:
        vec_inner.normalize()
        return vec_inner
    elif co_edges == 1:
        # No selected edges, one unselected edge.
        vec_inner.normalize()
        return vec_inner
    else:
        return None


def get_mirror_rail(mirror_plane, vec_up):
    p_norm = mirror_plane[1]
    mirror_rail = vec_up.cross(p_norm)
    if mirror_rail != ZERO_VEC:
        mirror_rail.normalize()
        # Project vec_up to mirror_plane
        vec_up = vec_up - vec_up.project(p_norm)
        vec_up.normalize()
        return mirror_rail, vec_up
    else:
        return None, vec_up


def get_vert_mirror_pairs(set_edges_orig, mirror_planes):
    if mirror_planes:
        set_edges_copy = set_edges_orig.copy()
        vert_mirror_pairs = dict()
        for e in set_edges_orig:
            v1, v2 = e.verts
            for mp in mirror_planes:
                p_co, p_norm, mlimit = mp
                v1_dist = abs(p_norm.dot(v1.co - p_co))
                v2_dist = abs(p_norm.dot(v2.co - p_co))
                if v1_dist <= mlimit:
                    # v1 is on a mirror plane.
                    vert_mirror_pairs[v1] = mp
                if v2_dist <= mlimit:
                    # v2 is on a mirror plane.
                    vert_mirror_pairs[v2] = mp
                if v1_dist <= mlimit and v2_dist <= mlimit:
                    # This edge is on a mirror_plane, so should not be offsetted.
                    set_edges_copy.remove(e)
        return vert_mirror_pairs, set_edges_copy
    else:
        return None, set_edges_orig


def collect_mirror_planes(ob_edit):
    mirror_planes = []
    eob_mat_inv = ob_edit.matrix_world.inverted()
    for m in ob_edit.modifiers:
        if (m.type == "MIRROR" and m.use_mirror_merge):
            merge_limit = m.merge_threshold
            if not m.mirror_object:
                loc = ZERO_VEC
                norm_x, norm_y, norm_z = X_UP, Y_UP, Z_UP
            else:
                mirror_mat_local = eob_mat_inv * m.mirror_object.matrix_world
                loc = mirror_mat_local.to_translation()
                norm_x, norm_y, norm_z, _ = mirror_mat_local.adjugated()
                norm_x = norm_x.to_3d().normalized()
                norm_y = norm_y.to_3d().normalized()
                norm_z = norm_z.to_3d().normalized()
            if m.use_x:
                mirror_planes.append((loc, norm_x, merge_limit))
            if m.use_y:
                mirror_planes.append((loc, norm_y, merge_limit))
            if m.use_z:
                mirror_planes.append((loc, norm_z, merge_limit))
    return mirror_planes


def collect_edges(bm):
    set_edges_orig = set()
    for e in bm.edges:
        if e.select:
            co_faces_selected = 0
            for f in e.link_faces:
                if f.select:
                    co_faces_selected += 1
                    if co_faces_selected == 2:
                        break
            else:
                set_edges_orig.add(e)

    if not set_edges_orig:
        return None

    return set_edges_orig


def collect_loops(set_edges_orig):
    set_edges_copy = set_edges_orig.copy()

    loops = []  # [v, e, v, e, ... , e, v]
    while set_edges_copy:
        edge_start = set_edges_copy.pop()
        v_left, v_right = edge_start.verts
        lp = [v_left, edge_start, v_right]
        reverse = False
        while True:
            edge = None
            for e in v_right.link_edges:
                if e in set_edges_copy:
                    if edge:
                        # Overlap detected.
                        return None
                    edge = e
                    set_edges_copy.remove(e)
            if edge:
                v_right = edge.other_vert(v_right)
                lp.extend((edge, v_right))
                continue
            else:
                if v_right is v_left:
                    # Real loop.
                    loops.append(lp)
                    break
                elif reverse is False:
                    # Right side of half loop.
                    # Reversing the loop to operate same procedure on the left side.
                    lp.reverse()
                    v_right, v_left = v_left, v_right
                    reverse = True
                    continue
                else:
                    # Half loop, completed.
                    loops.append(lp)
                    break
    return loops


def calc_loop_normal(verts, fallback=Z_UP):
    # Calculate normal from verts using Newell's method.
    normal = ZERO_VEC.copy()

    if verts[0] is verts[-1]:
        # Perfect loop
        range_verts = range(1, len(verts))
    else:
        # Half loop
        range_verts = range(0, len(verts))

    for i in range_verts:
        v1co, v2co = verts[i-1].co, verts[i].co
        normal.x += (v1co.y - v2co.y) * (v1co.z + v2co.z)
        normal.y += (v1co.z - v2co.z) * (v1co.x + v2co.x)
        normal.z += (v1co.x - v2co.x) * (v1co.y + v2co.y)

    if normal != ZERO_VEC:
        normal.normalize()
    else:
        normal = fallback

    return normal


def get_adj_faces(edges):
    adj_faces = []
    for e in edges:
        adj_f = None
        co_adj = 0
        for f in e.link_faces:
            # Search an adjacent face.
            # Selected face has precedance.
            if not f.hide and f.normal != ZERO_VEC:
                adj_exist = True
                adj_f = f
                co_adj += 1
                if f.select:
                    adj_faces.append(adj_f)
                    break
        else:
            if co_adj == 1:
                adj_faces.append(adj_f)
            else:
                adj_faces.append(None)
    return adj_faces


def get_directions(lp, vec_upward, normal_fallback, vert_mirror_pairs):
    opt_follow_face = False
    opt_edge_rail = False
    opt_er_only_end = False
    opt_threshold = radians(0.05)

    verts, edges = lp[::2], lp[1::2]
    set_edges = set(edges)
    lp_normal = calc_loop_normal(verts, fallback=normal_fallback)

    ##### Loop order might be changed below.
    if lp_normal.dot(vec_upward) < .0:
        # Make this loop's normal towards vec_upward.
        verts.reverse()
        edges.reverse()
        lp_normal *= -1

    if opt_follow_face:
        adj_faces = get_adj_faces(edges)
        verts, edges, lp_normal, adj_faces = reorder_loop(verts, edges, lp_normal, adj_faces)
    else:
        adj_faces = (None, ) * len(edges)
    ##### Loop order might be changed above.

    vec_edges = tuple((e.other_vert(v).co - v.co).normalized()
                      for v, e in zip(verts, edges))

    if verts[0] is verts[-1]:
        # Real loop. Popping last vertex.
        verts.pop()
        HALF_LOOP = False
    else:
        # Half loop
        HALF_LOOP = True

    len_verts = len(verts)
    directions = []
    for i in range(len_verts):
        vert = verts[i]
        ix_right, ix_left = i, i-1

        VERT_END = False
        if HALF_LOOP:
            if i == 0:
                # First vert
                ix_left = ix_right
                VERT_END = True
            elif i == len_verts - 1:
                # Last vert
                ix_right = ix_left
                VERT_END = True

        edge_right, edge_left = vec_edges[ix_right], vec_edges[ix_left]
        face_right, face_left = adj_faces[ix_right], adj_faces[ix_left]

        norm_right = face_right.normal if face_right else lp_normal
        norm_left = face_left.normal if face_left else lp_normal
        if norm_right.angle(norm_left) > opt_threshold:
            # Two faces are not flat.
            two_normals = True
        else:
            two_normals = False

        tan_right = edge_right.cross(norm_right).normalized()
        tan_left = edge_left.cross(norm_left).normalized()
        tan_avr = (tan_right + tan_left).normalized()
        norm_avr = (norm_right + norm_left).normalized()

        rail = None
        if two_normals or opt_edge_rail:
            # Get edge rail.
            # edge rail is a vector of an inner edge.
            if two_normals or (not opt_er_only_end) or VERT_END:
                rail = get_edge_rail(vert, set_edges)
        if vert_mirror_pairs and VERT_END:
            if vert in vert_mirror_pairs:
                rail, norm_avr = get_mirror_rail(vert_mirror_pairs[vert], norm_avr)
        if (not rail) and two_normals:
            # Get cross rail.
            # Cross rail is a cross vector between norm_right and norm_left.
            rail = get_cross_rail(tan_avr, edge_right, edge_left, norm_right, norm_left)
        if rail:
            dot = tan_avr.dot(rail)
            if dot > .0:
                tan_avr = rail
            elif dot < .0:
                tan_avr = -rail

        vec_plane = norm_avr.cross(tan_avr)
        e_dot_p_r = edge_right.dot(vec_plane)
        e_dot_p_l = edge_left.dot(vec_plane)
        if e_dot_p_r or e_dot_p_l:
            if e_dot_p_r > e_dot_p_l:
                vec_edge, e_dot_p = edge_right, e_dot_p_r
            else:
                vec_edge, e_dot_p = edge_left, e_dot_p_l

            vec_tan = (tan_avr - tan_avr.project(vec_edge)).normalized()
            # Make vec_tan perpendicular to vec_edge
            vec_up = vec_tan.cross(vec_edge)

            vec_width = vec_tan - (vec_tan.dot(vec_plane) / e_dot_p) * vec_edge
            vec_depth = vec_up - (vec_up.dot(vec_plane) / e_dot_p) * vec_edge
        else:
            vec_width = tan_avr
            vec_depth = norm_avr

        directions.append((vec_width, vec_depth))

    return verts, directions


def get_offset_infos(bm, ob_edit):
    time = perf_counter()

    set_edges_orig = collect_edges(bm)
    if set_edges_orig is None:
        raise Exception("No edges are selected.")
        return False, False

    vert_mirror_pairs = None

    loops = collect_loops(set_edges_orig)
    if loops is None:
        raise Exception("Overlapping edge loops detected. Select discrete edge loops")
        return False, False

    vec_upward = (X_UP + Y_UP + Z_UP).normalized()
    # vec_upward is used to unify loop normals when follow_face is off.
    normal_fallback = Z_UP
    #normal_fallback = Vector(context.region_data.view_matrix[2][:3])
    # normal_fallback is used when loop normal cannot be calculated.

    offset_infos = []
    for lp in loops:
        if selection_only:
            loop_is_selected = False
            for v in lp[::2]:  # iterate through verts
                if v.select:
                    loop_is_selected = True
                    break
            if not loop_is_selected:
                set_edges_orig.difference_update(lp[1::2])
                continue
        verts, directions = get_directions(lp, vec_upward, normal_fallback, vert_mirror_pairs)
        if verts:
            # convert vert objects to vert indexs
            for v, d in zip(verts, directions):
                offset_infos.append((v, v.co.copy(), d))

    edges_orig = list(set_edges_orig)
    deselect_geom(edges_orig)
    select_geom(bm.faces)

    # print("Preparing OffsetEdges: ", perf_counter() - time)

    return offset_infos, edges_orig


def extrude_and_pairing(bm, edges_orig, ref_verts):
    """ ref_verts is a list of vertices, each of which should be
    one end of an edge in edges_orig"""
    extruded = bmesh.ops.extrude_edge_only(bm, edges=edges_orig)["geom"]
    n_edges = n_faces = len(edges_orig)
    n_verts = len(extruded) - n_edges - n_faces

    exverts = set(extruded[:n_verts])
    exedges = set(extruded[n_verts:n_verts + n_edges])
    #faces = set(extruded[n_verts + n_edges:])
    side_edges = set(e for v in exverts for e in v.link_edges if e not in exedges)

    # ref_verts[i] and ret[i] are both ends of a side edge.
    exverts_ordered = \
        [e.other_vert(v) for v in ref_verts for e in v.link_edges if e in side_edges]

    return exverts_ordered, list(exedges), list(side_edges)


def move_verts(bm, me, width, depth, offset_infos, verts_offset=None, update=True):
    if verts_offset is None:
        for v, co, (vec_w, vec_d) in offset_infos:
            v.co = co + width * vec_w + depth * vec_d
    else:
        for (_, co, (vec_w, vec_d)), v in zip(offset_infos, verts_offset):
            v.co = co + width * vec_w + depth * vec_d

    if update:
        bm.normal_update()
        bmesh.update_edit_mesh(me)


def get_exverts(offset_infos, edges_orig):
    ref_verts = [v for v, _, _ in offset_infos]

    exverts = ref_verts
    exedges = edges_orig

    for e in exedges:
        e.select = True

    return exverts

def do_offset(bm, width, depth, angle, offset_infos, verts_offset, depth_mode):
    w = with
    if depth_mode == "angle":
        width = w * cos(angle)
        depth = w * sin(angle)

    move_verts(bm, width, depth, offset_infos, verts_offset)

def mesh_offset(bme, with, angle=0, depth=0, selection_only=False, depth_mode="angle"):  # depth_mode: angle/depth
    offset_infos, edges_orig = get_offset_infos(bme, selection_only)
    exverts = get_exverts(offset_infos, edges_orig)
    do_offset(bme, width, depth, angle, offset_infos, exverts, depth_mode)

# def modal_prepare_bmeshes(self, context, ob_edit):
#     bpy.ops.object.mode_set(mode="OBJECT")
#     self._bm_orig = bmesh.new()
#     self._bm_orig.from_mesh(ob_edit.data)
#     bpy.ops.object.mode_set(mode="EDIT")
#
#     self._bm = bmesh.from_edit_mesh(ob_edit.data)
#
#     self._offset_infos, self._edges_orig = \
#         self.get_offset_infos(self._bm, ob_edit)
#     if self._offset_infos is False:
#         return False
#     self._exverts = \
#         self.get_exverts(self._bm, self._offset_infos, self._edges_orig)
#
#     return True
#
# def modal_clean_bmeshes(self, context, ob_edit):
#     bpy.ops.object.mode_set(mode="OBJECT")
#     self._bm_orig.to_mesh(ob_edit.data)
#     bpy.ops.object.mode_set(mode="EDIT")
#     self._bm_orig.free()
#     self._bm.free()
#
# def get_factor(self, context, edges_orig):
#     """get the length in the space of edited object
#     which correspond to 1px of 3d view. This method
#     is used to convert the distance of mouse movement
#     to offsetting width in interactive mode.
#     """
#     ob = context.edit_object
#     mat_w = ob.matrix_world
#     reg = context.region
#     reg3d = context.space_data.region_3d  # Don't use context.region_data
#                                           # because this will cause error
#                                           # when invoked from header menu.
#
#     co_median = Vector((0, 0, 0))
#     for e in edges_orig:
#         co_median += e.verts[0].co
#     co_median /= len(edges_orig)
#     depth_loc = mat_w * co_median  # World coords of median point
#
#     win_left = Vector((0, 0))
#     win_right = Vector((reg.width, 0))
#     left = view3d_utils.region_2d_to_location_3d(reg, reg3d, win_left, depth_loc)
#     right = view3d_utils.region_2d_to_location_3d(reg, reg3d, win_right, depth_loc)
#     vec_width = mat_w.inverted_safe() * (right - left)  # width vector in the object space
#     width_3d = vec_width.length   # window width in the object space
#
#     return width_3d / reg.width
