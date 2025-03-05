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
from operator import mul
from functools import reduce

# Blender imports
from mathutils import Matrix, Vector

# Module imports
# NONE!


def mathutils_mult(*argv):
    """ elementwise multiplication for vectors, matrices, etc. """
    result = argv[0]
    for arg in argv[1:]:
        result = result @ arg
    return result


def vec_mult(v1:Vector, v2:Vector, outer_type=Vector):
    """ componentwise multiplication for vectors """
    return outer_type(e1 * e2 for e1, e2 in zip(v1, v2))


def vec_div(v1:Vector, v2:Vector, outer_type=Vector):
    """ componentwise division for vectors """
    return outer_type(e1 / e2 for e1, e2 in zip(v1, v2))


def vec_remainder(v1:Vector, v2:Vector, outer_type=Vector):
    """ componentwise remainder for vectors """
    return outer_type(e1 % e2 for e1, e2 in zip(v1, v2))


def vec_abs(v1:Vector, outer_type:type=Vector):
    """ componentwise absolute value for vectors """
    return outer_type(abs(e1) for e1 in v1)


def vec_clamp(v1:Vector, outer_type=Vector):
    """ componentwise clamping value for vectors """
    return outer_type(max(0, min(1, e1)) for e1 in v1)


def vec_conv(v1:Vector, inner_type:type=int, outer_type:type=Vector):
    """ convert type of items in iterable """
    return outer_type([inner_type(e1) for e1 in v1])


def vec_round(v1:Vector, precision:int=0, round_type:str="ROUND", outer_type:type=Vector):
    """ round items in Vector """
    if round_type == "ROUND":
        lst = [round(e1, precision) for e1 in v1]
    elif round_type == "FLOOR":
        prec = 10**precision
        lst = [math.floor(e1 * prec) / prec for e1 in v1] if prec != 1 else [math.floor(e1) for e1 in v1]
    elif round_type in ("CEILING", "CEIL"):
        prec = 10**precision
        lst = [math.ceil(e1 * prec) / prec for e1 in v1] if prec != 1 else [math.ceil(e1) for e1 in v1]
    else:
        raise Exception("Argument passed to 'round_type' parameter invalid: " + str(round_type))
    return outer_type(lst)


def outer_type(v1:Vector, outer_type:type=Vector):
    """ clamp items in iterable to the 0..1 range """
    return outer_type([max(0, min(1, e1)) for e1 in v1])


def vec_dist(v1:Vector, v2:Vector):
    """ distance between two points """
    assert len(v1) == len(v2)
    lst = [(e1 - e2) ** 2 for e1, e2 in zip(v1, v2)]
    return math.sqrt(sum(lst))


def vec_interp(v1:Vector, v2:Vector, fac:float, outer_type:type=Vector):
    return outer_type([(e1 * (1 - fac)) + (e2 * fac) for e1, e2 in zip(v1, v2)])


def mx_2d_to_3d(mx_3x3:Matrix):
    mx_4x4 = Matrix.Identity(4)
    mx_4x4[0][:2] = mx_3x3[0][:2]
    mx_4x4[1][:2] = mx_3x3[1][:2]
    mx_4x4[0][3] = mx_3x3[0][2]
    mx_4x4[1][3] = mx_3x3[1][2]
    mx_4x4[3][:2] = mx_3x3[2][:2]
    return mx_4x4


# available at: `from statistics import mean`
# def mean(lst:list):
#     """ mean of a list """
#     return sum(lst)/len(lst)


def prod(lst:list):
    """ product of a list """
    return reduce(mul, lst)


def round_nearest(num:float, divisor:int, round_type:str="ROUND"):
    """ round to nearest multiple of 'divisor' """
    rem = num % divisor
    if round_type == "FLOOR":
        return round_down(num, divisor)
    elif round_type in ("CEILING", "CEIL") or rem > divisor / 2:
        return round_up(num, divisor)
    else:
        div_str = str(divisor)
        prec = 0 if "." not in div_str else len(div_str.split(".")[1])
        return round(divisor * round(num / divisor), prec)


def round_up(num:float, divisor:int):
    """ round up to nearest multiple of 'divisor' """
    return num + divisor - (num % divisor)


def round_down(num:float, divisor:int):
    """ round down to nearest multiple of 'divisor' """
    return num - (num % divisor)
