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

# System imports
import math

# Blender imports
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
from bpy.types import Object

# Module imports
from .blender import *
from .maths import mathutils_mult
from .python_utils import confirm_iter


def apply_transform(obj:Object, location:bool=True, rotation:bool=True, scale:bool=True):
    """ apply object transformation to mesh """
    loc, rot, scl = obj.matrix_world.decompose()
    obj.matrix_world = Matrix.Identity(4)
    m = obj.data
    if scale:
        s_mat_x = Matrix.Scale(scl.x, 4, Vector((1, 0, 0)))
        s_mat_y = Matrix.Scale(scl.y, 4, Vector((0, 1, 0)))
        s_mat_z = Matrix.Scale(scl.z, 4, Vector((0, 0, 1)))
        m.transform(mathutils_mult(s_mat_x, s_mat_y, s_mat_z))
    else:
        obj.scale = scl
    if rotation:
        m.transform(rot.to_matrix().to_4x4())
    else:
        obj.rotation_euler = rot.to_euler()
    if location:
        m.transform(Matrix.Translation(loc))
    else:
        obj.location = loc


def parent_clear(objs, apply_transform:bool=True):
    """ efficiently clear parent """
    # select(objs, active=True, only=True)
    # bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    objs = confirm_iter(objs)
    if apply_transform:
        for obj in objs:
            last_mx = obj.matrix_world.copy()
            obj.parent = None
            obj.matrix_world = last_mx
    else:
        for obj in objs:
            obj.parent = None


def children_clear(parent:Object, apply_transform:bool=True):
    """clear all children of an object"""
    for obj in parent.children:
        parent_clear(obj, apply_transform=apply_transform)


def parent_set(objs:list, parent:Object, keep_transform:bool=False):
    """ efficiently set parent for obj(s) """
    objs = confirm_iter(objs)
    if keep_transform:
        for obj in objs:
            last_mx = obj.matrix_world.copy()
            obj.parent = parent
            obj.matrix_world = last_mx
    else:
        for obj in objs:
            obj.parent = parent


def get_bounds(coords:list):
    """ brute force method for obtaining bounding box from list of coords """
    # initialize min and max
    min = Vector((math.inf, math.inf, math.inf))
    max = Vector((-math.inf, -math.inf, -math.inf))
    # calculate min and max verts
    for co in coords:
        if co.x > max.x:
            max.x = co.x
        if co.x < min.x:
            min.x = co.x
        if co.y > max.y:
            max.y = co.y
        if co.y < min.y:
            min.y = co.y
        if co.z > max.z:
            max.z = co.z
        if co.z < min.z:
            min.z = co.z
    # set up bounding box list of coord lists
    bound_box = [
        list(min),
        [min.x, min.y, max.z],
        [min.x, max.y, max.z],
        [min.x, max.y, min.z],
        [max.x, min.y, min.z],
        [max.x, min.y, max.z],
        list(max),
        [max.x, max.y, min.z],
    ]
    return bound_box


def bounds(obj:Object, local:bool=False, use_adaptive_domain:bool=True):
    """
    returns object details with the following subattribute Vectors:

    .max : maximum value of object
    .min : minimum value of object
    .mid : midpoint value of object
    .dist: distance min to max

    """

    local_coords = get_bounds([v.co for v in obj.data.vertices]) if is_smoke(obj) and is_adaptive(obj) and not use_adaptive_domain else obj.bound_box[:]
    om = obj.matrix_world

    if not local:
        worldify = lambda p: mathutils_mult(om, Vector(p[:]))
        coords = [worldify(p).to_tuple() for p in local_coords]
    else:
        coords = [p[:] for p in local_coords]

    rotated = zip(*coords[::-1])
    get_max = lambda i: max([co[i] for co in coords])
    get_min = lambda i: min([co[i] for co in coords])

    info = lambda: None
    info.max = Vector((get_max(0), get_max(1), get_max(2)))
    info.min = Vector((get_min(0), get_min(1), get_min(2)))
    info.mid = (info.min + info.max) / 2
    info.dist = info.max - info.min

    return info


def set_obj_origin(obj:Object, loc:tuple):
    """ set object origin """
    l, r, s = obj.matrix_world.decompose()
    r_mat = r.to_matrix().to_4x4()
    s_mat_x = Matrix.Scale(s.x, 4, Vector((1, 0, 0)))
    s_mat_y = Matrix.Scale(s.y, 4, Vector((0, 1, 0)))
    s_mat_z = Matrix.Scale(s.z, 4, Vector((0, 0, 1)))
    s_mat = mathutils_mult(s_mat_x, s_mat_y, s_mat_z)
    mx = mathutils_mult((obj.matrix_world.translation - Vector(loc)), r_mat, s_mat.inverted())
    obj.data.transform(Matrix.Translation(mx))
    obj.matrix_world.translation = loc


def transform_to_world(vec:Vector, mat:Matrix, junk_bme:bmesh=None):
    """ transfrom vector to world space from 'mat' matrix local space """
    # decompose matrix
    loc = mat.to_translation()
    rot = mat.to_euler()
    scale = mat.to_scale()[0]
    # apply rotation
    if rot != Euler((0, 0, 0), "XYZ"):
        junk_bme = bmesh.new() if junk_bme is None else junk_bme
        v1 = junk_bme.verts.new(vec)
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=-loc, matrix=Matrix.Rotation(rot.x, 3, "X"))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=-loc, matrix=Matrix.Rotation(rot.y, 3, "Y"))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=-loc, matrix=Matrix.Rotation(rot.z, 3, "Z"))
        vec = v1.co
    # apply scale
    vec = vec * scale
    # apply translation
    vec += loc
    return vec


def transform_to_local(vec:Vector, mat:Matrix, junk_bme:bmesh=None):
    """ transfrom vector to local space of 'mat' matrix """
    # decompose matrix
    loc = mat.to_translation()
    rot = mat.to_euler()
    scale = mat.to_scale()[0]
    # apply scale
    vec = vec / scale
    # apply rotation
    if rot != Euler((0, 0, 0), "XYZ"):
        junk_bme = bmesh.new() if junk_bme is None else junk_bme
        v1 = junk_bme.verts.new(vec)
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=loc, matrix=Matrix.Rotation(-rot.z, 3, "Z"))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=loc, matrix=Matrix.Rotation(-rot.y, 3, "Y"))
        bmesh.ops.rotate(junk_bme, verts=[v1], cent=loc, matrix=Matrix.Rotation(-rot.x, 3, "X"))
        vec = v1.co
    return vec
