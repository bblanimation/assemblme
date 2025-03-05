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
try:
    from shapely.geometry import Point, Polygon, MultiPoint
except ModuleNotFoundError:
    print("'shapely' python module not installed")

# Blender imports
from mathutils import Vector

# Module imports
# NONE!


def polynpoly(poly_coords1:list, poly_coords2:list):
    """ check if one polygon is contained inside another (does not account for concavity) """
    poly2 = MultiPoint(poly_coords2).convex_hull
    for coord in poly_coords1:
        point = Point(coord)
        if not poly2.contains(point):
            return False
    return True


def pointnpoly(point_coord:Vector, poly_coords:list):
    poly = MultiPoint(poly_coords).convex_hull
    point = Point(point_coord)
    return poly.contains(point)


def get_poly_area(poly_coords:list):
    def segments(p):
        return zip(p, p[1:] + [p[0]])
    return 0.5 * abs(sum(x0 * y1 - x1 * y0 for ((x0, y0, z0), (x1, y1, z1)) in segments(poly_coords)))
