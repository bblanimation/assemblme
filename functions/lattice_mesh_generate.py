# Copyright (C) 2025 Christopher Gearhart
# chris@bricksbroughttolife.com
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
import numpy as np

# Blender imports
import bpy
import bmesh
from mathutils import Matrix, Vector

# Module imports
from .common import *

def generate_lattice(vert_dist:Vector, scale:Vector, offset:Vector=Vector((0, 0, 0)), extra_res:int=0, visualize:bool=False):
    """ return lattice coordinate matrix surrounding object of size 'scale'

    Keyword arguments:
    vert_dist  -- distance between lattice verts in 3D space
    scale     -- lattice scale in 3D space
    offset    -- offset lattice center from origin
    extra_res -- additional resolution to add to ends of lattice
    visualize -- draw lattice coordinates in 3D space

    """

    # calculate res of lattice
    res = Vector((scale.x / vert_dist.x,
                  scale.y / vert_dist.y,
                  scale.z / vert_dist.z))
    # round up lattice res
    res = Vector(round_up(round(val), 2) for val in res)
    h_res = res / 2
    # populate coord matrix
    nx, ny, nz = round(res.x) - 1 + extra_res, round(res.y) - 1 + extra_res, round(res.z) - 1 + extra_res
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

    if visualize:
        # draw bmesh verts in 3D space
        draw_bmesh(bme)

    return bme
