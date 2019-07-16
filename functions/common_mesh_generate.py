# Copyright (C) 2019 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
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
import numpy as np

# Blender imports
import bpy
import bmesh
from mathutils import Matrix, Vector

# Addon imports
from .common import *

def make_square(coord1:Vector, coord2:Vector, face:bool=True, flip_normal:bool=False, bme:bmesh=None):
    """
    create a square with bmesh

    Keyword Arguments:
        coord1      -- back/left/bottom corner of the square (furthest negative in all three axes)
        coord2      -- front/right/top  corner of the square (furthest positive in all three axes)
        face        -- draw face connecting cube verts
        flip_normal -- flip the normals of the cube
        bme         -- bmesh object in which to create verts
    NOTE: if coord1 and coord2 are different on all three axes, z axis will stay consistent at coord1.z

    Returns:
        v_list      -- list of vertices with normal facing in positive direction (right hand rule)

    """
    # create new bmesh object
    bme = bme or bmesh.new()

    # create square with normal facing +x direction
    if coord1.x == coord2.x:
        v1, v2, v3, v4 = [bme.verts.new((coord1.x, y, z)) for y in [coord1.y, coord2.y] for z in [coord1.z, coord2.z]]
    # create square with normal facing +y direction
    elif coord1.y == coord2.y:
        v1, v2, v3, v4 = [bme.verts.new((x, coord1.y, z)) for x in [coord1.x, coord2.x] for z in [coord1.z, coord2.z]]
    # create square with normal facing +z direction
    else:
        v1, v2, v3, v4 = [bme.verts.new((x, y, coord1.z)) for x in [coord1.x, coord2.x] for y in [coord1.y, coord2.y]]
    v_list = [v1, v3, v4, v2]

    # create face
    if face:
        bme.faces.new(v_list[::-1] if flip_normal else v_list)

    return v_list


def make_cube(coord1:Vector, coord2:Vector, sides:list=[False]*6, flip_normals:bool=False, bme:bmesh=None):
    """
    create a cube with bmesh

    Keyword Arguments:
        coord1      -- back/left/bottom corner of the cube (furthest negative in all three axes)
        coord2      -- front/right/top  corner of the cube (furthest positive in all three axes)
        sides       -- draw sides [+z, -z, +x, -x, +y, -y]
        flip_normals -- flip the normals of the cube
        bme         -- bmesh object in which to create verts

    Returns:
        v_list       -- list of vertices in the following x,y,z order: [---, -+-, ++-, +--, --+, +-+, +++, -++]

    """

    # ensure coord1 is less than coord2 in all dimensions
    assert coord1.x < coord2.x
    assert coord1.y < coord2.y
    assert coord1.z < coord2.z

    # create new bmesh object
    bme = bme or bmesh.new()

    # create vertices
    v_list = [bme.verts.new((x, y, z)) for x in [coord1.x, coord2.x] for y in [coord1.y, coord2.y] for z in [coord1.z, coord2.z]]

    # create faces
    v1, v2, v3, v4, v5, v6, v7, v8 = v_list
    new_faces = []
    if sides[0]:
        new_faces.append([v6, v8, v4, v2])
    if sides[1]:
        new_faces.append([v3, v7, v5, v1])
    if sides[4]:
        new_faces.append([v4, v8, v7, v3])
    if sides[3]:
        new_faces.append([v2, v4, v3, v1])
    if sides[2]:
        new_faces.append([v8, v6, v5, v7])
    if sides[5]:
        new_faces.append([v6, v2, v1, v5])

    for f in new_faces:
        if flip_normals:
            f.reverse()
        bme.faces.new(f)

    return [v1, v3, v7, v5, v2, v6, v8, v4]


def make_circle(radius:float, num_verts:int, co:Vector=Vector((0,0,0)), face:bool=True, flip_normals:bool=False, bme:bmesh=None):
    """
    create a circle with bmesh

    Keyword Arguments:
        radius       -- radius of circle
        num_verts    -- number of verts on circumference
        co           -- coordinate of cylinder's center
        face         -- create face between circle verts
        flip_normals -- flip normals of cylinder
        bme          -- bmesh object in which to create verts

    """
    # initialize vars
    bme = bme or bmesh.new()
    verts = []

    # create verts around circumference of circle
    for i in range(num_verts):
        circ_val = ((2 * math.pi) / num_verts) * i
        x = radius * math.cos(circ_val)
        y = radius * math.sin(circ_val)
        coord = co + Vector((x, y, 0))
        verts.append(bme.verts.new(coord))
    # create face
    if face:
        bme.faces.new(verts if not flip_normals else verts[::-1])

    return verts


def make_cylinder(radius:float, height:float, num_verts:int, co:Vector=Vector((0,0,0)), bot_face:bool=True, top_face:bool=True, flip_normals:bool=False, bme:bmesh=None):
    """
    create a cylinder with bmesh

    Keyword Arguments:
        radius       -- radius of cylinder
        height       -- height of cylinder
        num_verts    -- number of verts per circle
        co           -- coordinate of cylinder's center
        bot_face     -- create face on bottom of cylinder
        top_face     -- create face on top of cylinder
        flip_normals -- flip normals of cylinder
        bme          -- bmesh object in which to create verts

    """
    # initialize vars
    bme = bme or bmesh.new()
    top_verts = []
    bot_verts = []
    side_faces = []
    z = height / 2

    # create upper and lower circles
    for i in range(num_verts):
        circ_val = ((2 * math.pi) / num_verts) * i
        x = radius * math.cos(circ_val)
        y = radius * math.sin(circ_val)
        coord_t = co + Vector((x, y, z))
        coord_b = co + Vector((x, y, -z))
        top_verts.append(bme.verts.new(coord_t))
        bot_verts.append(bme.verts.new(coord_b))

    # create faces on the sides
    _, side_faces = connect_circles(top_verts if flip_normals else bot_verts, bot_verts if flip_normals else top_verts, bme)
    smooth_bm_faces(side_faces)

    # create top and bottom faces
    if top_face:
        bme.faces.new(top_verts if not flip_normals else top_verts[::-1])
    if bot_face:
        bme.faces.new(bot_verts[::-1] if not flip_normals else bot_verts)

    # return bme & dictionary with lists of top and bottom vertices
    return bme, {"bottom":bot_verts[::-1], "top":top_verts}


def make_tube(radius:float, height:float, thickness:float, num_verts:int, co:Vector=Vector((0,0,0)), top_face:bool=True, bot_face:bool=True, bme:bmesh=None):
    """
    create a tube with bmesh

    Keyword Arguments:
        radius    -- radius of inner cylinder
        height    -- height of cylinder
        thickness -- thickness of tube
        num_verts -- number of verts per circle
        co        -- coordinate of cylinder's center
        bot_face  -- create face on bottom of cylinder
        top_face  -- create face on top of cylinder
        bme       -- bmesh object in which to create verts

    """
    # create new bmesh object
    if bme == None:
        bme = bmesh.new()

    # create upper and lower circles
    bme, inner_verts = make_cylinder(radius, height, num_verts, co=co, bot_face=False, top_face=False, flip_normals=True, bme=bme)
    bme, outer_verts = make_cylinder(radius + thickness, height, num_verts, co=co, bot_face=False, top_face=False, bme=bme)
    if top_face:
        connect_circles(outer_verts["top"], inner_verts["top"], bme)
    if bot_face:
        connect_circles(outer_verts["bottom"], inner_verts["bottom"], bme)

    # return bmesh
    return bme, {"outer":outer_verts, "inner":inner_verts}


def make_tetra():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    v1 = bme.verts.new((0, 1, -1))
    v2 = bme.verts.new((0.86603, -0.5, -1))
    v3 = bme.verts.new((-0.86603, -0.5, -1))
    bme.faces.new((v1, v2, v3))
    v4 = bme.verts.new((0, 0, 1))
    bme.faces.new((v4, v3, v2))
    bme.faces.new((v4, v1, v3))
    bme.faces.new((v4, v2, v1))

    # return bmesh
    return bme


def make_cone(radius, num_verts):
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    top_v = bme.verts.new((0, 0, 1))
    # create bottom circle
    vertList = []
    for i in range(num_verts):
        vertList.append(bme.verts.new((radius * math.cos(((2 * math.pi) / num_verts) * i), radius * math.sin(((2 * math.pi) / num_verts) * i), -1)))
    bme.faces.new(vertList)

    bme.faces.new((vertList[-1], vertList[0], top_v))
    for v in range(num_verts-1):
        bme.faces.new((vertList.pop(0), vertList[0], top_v))

    # return bmesh
    return bme


def make_octa():
    # create new bmesh object
    bme = bmesh.new()

    # make vertices
    top_v = bme.verts.new((0, 0, 1.5))
    bot_v = bme.verts.new((0, 0,-1.5))

    v1 = bme.verts.new(( 1, 1, 0))
    v2 = bme.verts.new((-1, 1, 0))
    v3 = bme.verts.new((-1,-1, 0))
    v4 = bme.verts.new(( 1,-1, 0))

    # make faces
    bme.faces.new((top_v, v1, v2))
    bme.faces.new((bot_v, v2, v1))
    bme.faces.new((top_v, v2, v3))
    bme.faces.new((bot_v, v3, v2))
    bme.faces.new((top_v, v3, v4))
    bme.faces.new((bot_v, v4, v3))
    bme.faces.new((top_v, v4, v1))
    bme.faces.new((bot_v, v1, v4))

    # return bmesh
    return bme


def make_dodec():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    q = 1.618
    bme.verts.new(( 1,      1,      1))
    bme.verts.new((-1,     -1,     -1))
    bme.verts.new((-1,      1,      1))
    bme.verts.new(( 1,     -1,      1))
    bme.verts.new(( 1,      1,     -1))
    bme.verts.new(( 1,     -1,     -1))
    bme.verts.new((-1,     -1,      1))
    bme.verts.new((-1,      1,     -1))
    bme.verts.new(( 0,      1 / q,  q))
    bme.verts.new(( 0,     -1 / q,  q))
    bme.verts.new(( 0,      1 / q, -q))
    bme.verts.new(( 0,     -1 / q, -q))
    bme.verts.new(( 1 / q,  q,      0))
    bme.verts.new(( 1 / q, -q,      0))
    bme.verts.new((-1 / q,  q,      0))
    bme.verts.new((-1 / q, -q,      0))
    bme.verts.new(( q,      0,      1 / q))
    bme.verts.new((-q,      0,      1 / q))
    bme.verts.new(( q,      0,     -1 / q))
    bme.verts.new((-q,      0,     -1 / q))

    # return bmesh
    return bme


def make_uv_sphere(radius, segments, rings):
    # create new bmesh object
    bme = bmesh.new()
    test_bme = bmesh.new()

    # create vertices
    vert_list_v = []
    vert_list_h = []
    for i in range(int(segments / 4), int((3 * segments) / 4) + 1):
        vert = test_bme.verts.new((radius * math.cos(((2 * math.pi) / segments) * i), 0, radius * math.sin(((2 * math.pi) / segments) * i)))
        vert_list_v.append(v)
        next_vert_list_h = []
        if i != int(segments / 4) and i != int((3 * segments) / 4):
            for j in range(segmentsrings):
                # replace 'r' with x value of 'segments'
                next_vert_list_h.append(bme.verts.new((v.co.x * math.cos(((2 * math.pi) / rings) * j), v.co.x * math.sin(((2 * math.pi) / rings) * j), v.co.z)))
            vert_list_h.append(next_vert_list_h)
        elif i == int(segments / 4):
            top_v = bme.verts.new((v.co))
        elif i == int((3 * segments) / 4):
            bot_v = bme.verts.new((v.co))

    # create faces
    for l in range(len(vert_list_h) - 1):
        for m in range(-1, len(vert_list_h[l]) - 1):
            bme.faces.new((vert_list_h[l][m], vert_list_h[l + 1][m], vert_list_h[l + 1][m + 1], vert_list_h[l][m + 1]))

    # create top and bottom faces
    for n in range(-1, rings - 1):
        bme.faces.new((vert_list_h[0][n], vert_list_h[0][n + 1], top_v))
        bme.faces.new((vert_list_h[-1][n + 1], vert_list_h[-1][n], bot_v))

    # return bmesh
    return bme


def make_ico():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    top_v = bme.verts.new((0, 0, 1))
    r1a = bme.verts.new((0.28, 0.85, 0.45))
    r1b = bme.verts.new((-0.72, 0.53, 0.45))
    bme.faces.new((r1a, r1b, top_v))
    r1c = bme.verts.new((-0.72, -0.53, 0.45))
    bme.faces.new((r1b, r1c, top_v))
    r1d = bme.verts.new((0.28, -0.85, 0.45))
    bme.faces.new((r1c, r1d, top_v))
    r1e = bme.verts.new((0.89, 0, 0.45))
    bme.faces.new((r1d, r1e, top_v))
    bme.faces.new((r1e, r1a, top_v))
    bot_v = bme.verts.new((0, 0,-1))
    r2a = bme.verts.new((0.72, 0.53, -0.45))
    r2b = bme.verts.new((-0.28, 0.85, -0.45))
    bme.faces.new((r2b, r2a, bot_v))
    r2c = bme.verts.new((-0.89, 0, -0.45))
    bme.faces.new((r2c, r2b, bot_v))
    r2d = bme.verts.new((-0.28, -0.85, -0.45))
    bme.faces.new((r2d, r2c, bot_v))
    r2e = bme.verts.new((0.72, -0.53, -0.45))
    bme.faces.new((r2e, r2d, bot_v))
    bme.faces.new((r2a, r2e, bot_v))

    bme.faces.new((r2a, r2b, r1a))
    bme.faces.new((r2b, r2c, r1b))
    bme.faces.new((r2c, r2d, r1c))
    bme.faces.new((r2d, r2e, r1d))
    bme.faces.new((r2e, r2a, r1e))

    bme.faces.new((r1a, r2b, r1b))
    bme.faces.new((r1b, r2c, r1c))
    bme.faces.new((r1c, r2d, r1d))
    bme.faces.new((r1d, r2e, r1e))
    bme.faces.new((r1e, r2a, r1a))

    # return bmesh
    return bme


def make_trunc_ico(layer):
    new_obj_from_bmesh(layer, make_ico(), "truncated icosahedron")
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.bevel(offset=0.35, vertex_only=True)
    bpy.ops.object.editmode_toggle()


def tuple_add(p1, p2):
    """ returns linear sum of two given tuples """
    return tuple(x+y for x,y in zip(p1, p2))


def make_lattice(vert_dist:Vector, scale:Vector, offset:Vector=Vector((0, 0, 0)), extra_res:int=0, visualize:bool=False):
    """ return lattice bmesh surrounding object of size 'scale'

    Keyword arguments:
    vert_dist -- distance between lattice verts in 3D space
    scale     -- lattice scale in 3D space
    offset    -- offset lattice center from origin
    extra_res -- additional resolution to add to ends of lattice
    visualize -- draw lattice coordinates in 3D space

    """

    # shift offset to ensure lattice surrounds object
    offset = offset - vec_remainder(offset, vert_dist)
    # calculate res of lattice
    res = Vector((scale.x / vert_dist.x,
                  scale.y / vert_dist.y,
                  scale.z / vert_dist.z))
    # round up lattice res
    res = Vector(round_up(round(val), 2) for val in res)
    h_res = res / 2
    # populate coord matrix
    nx, ny, nz = int(res.x) - 1 + extra_res, int(res.y) - 1 + extra_res, int(res.z) - 1 + extra_res
    create_coord = lambda v: vec_mult(v - h_res, vert_dist) + offset
    coord_matrix = [[[create_coord(Vector((x, y, z))) for z in range(nz)] for y in range(ny)] for x in range(nx)]

    # create bmesh
    bme = bmesh.new()
    vert_matrix = np.zeros((len(coord_matrix), len(coord_matrix[0]), len(coord_matrix[0][0]))).tolist()
    # add vertex for each coordinate
    for x in range(len(coord_matrix)):
        for y in range(len(coord_matrix[0])):
            for z in range(len(coord_matrix[0][0])):
                vert_matrix[x][y][z] = bme.verts.new(coord_matrix[x][y][z])
                # create new edges from vert
                if x != 0: bme.edges.new((vert_matrix[x][y][z], vert_matrix[x-1][y][z]))
                if y != 0: bme.edges.new((vert_matrix[x][y][z], vert_matrix[x][y-1][z]))
                if z != 0: bme.edges.new((vert_matrix[x][y][z], vert_matrix[x][y][z-1]))
    # draw bmesh verts in 3D space
    if visualize:
        draw_bmesh(bme)

    return bme
