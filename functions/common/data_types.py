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
from colorsys import rgb_to_hsv, hsv_to_rgb
from os.path import join, dirname, basename
import numpy as np
import time
import types as py_types

# Blender imports
import bpy
from bpy.types import bpy_prop_array
import bmesh
from mathutils import Vector, Color

# Module imports
from .blender import link_object
from .images import *
from .maths import *
from .paths import *
from .python_utils import *
from .reporting import stopwatch
# from .shapes import polynpoly
from .transform import get_bounds


class Vector2:
    """ Implementation of the mathutils 'Vector' data type that supports double precision """
    def __init__(self, value=(0, 0, 0)):
        assert type(value) in (tuple, list, Vector, Vector2, py_types.GeneratorType, bpy_prop_array)
        if type(value) in (Vector, Color, bpy_prop_array):
            self._seq = [round(i, 6) for i in value]
        else:
            self._seq = list(value)

    def __str__(self):
        return "<Vector2(" + str(tuple(self._seq)) + ")>"

    def __neg__(self):
        return Vector2([-i for i in self._seq])

    def __pos__(self):
        return self.copy()

    def __abs__(self):
        return Vector2([abs(i) for i in self._seq])

    def __add__(self, other):
        new_vec = Vector2(self.to_list())
        if type(other) in (Vector2, Vector):
            assert len(self) == len(other)
            for i in range(len(new_vec)):
                new_vec[i] += other[i]
        elif type(other) in (float, int):
            for i in range(len(new_vec)):
                new_vec[i] += other
        else:
            raise Exception("Vector2 addition: (Vector2 and {}) invalid type for this operation").format(type(other))
        return new_vec

    def __sub__(self, other):
        new_vec = Vector2(self.to_list())
        if type(other) in (Vector2, Vector):
            assert len(self) == len(other)
            for i in range(len(new_vec)):
                new_vec[i] -= other[i]
        elif type(other) in (float, int):
            for i in range(len(new_vec)):
                new_vec[i] -= other
        else:
            raise Exception("Vector2 subtraction: (Vector2 and {}) invalid type for this operation").format(type(other))
        return new_vec

    def __mul__(self, other):
        new_vec = Vector2(self.to_list())
        if type(other) in (Vector2, Vector):
            assert len(self) == len(other)
            for i in range(len(new_vec)):
                new_vec[i] *= other[i]
        elif type(other) in (float, int):
            for i in range(len(new_vec)):
                new_vec[i] *= other
        else:
            raise Exception("Vector2 multiplication: (Vector2 and {}) invalid type for this operation").format(type(other))
        return new_vec

    def __div__(self, other):
        new_vec = Vector2(self.to_list())
        if type(other) in (Vector2, Vector):
            assert len(self) == len(other)
            for i in range(len(new_vec)):
                new_vec[i] /= other[i]
        elif type(other) in (int, float):
            for i in range(len(new_vec)):
                new_vec[i] /= other
        else:
            raise Exception("Vector2 division: (Vector2 and {}) invalid type for this operation")
        return new_vec

    def __truediv__(self, other):
        return self.__div__(other)

    def __len__(self):
        return len(self._seq)

    def __setitem__(self, key, val):
        assert type(key) in (int, slice)
        if isinstance(key, int):
            self._seq[key] = val
        else:
            self._seq[key.start:key.stop:key.step] = val

    def __getitem__(self, key):
        assert type(key) in (int, slice)
        if isinstance(key, int):
            return self._seq[key]
        else:
            return self._seq[key.start:key.stop:key.step]

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self):
        if self._idx < len(self._seq):
            result = self._seq[self._idx]
            self._idx += 1
            return result
        else:
            raise StopIteration

    def to_list(self):
        return self._seq.copy()

    def to_tuple(self):
        return tuple(self._seq)

    def to_3d(self):
        if self.length == 2:
            return Vector2(self._seq + [0])
        else:
            return Vector2(self._seq[:3])

    def dot(self, vec):
        assert len(vec) == len(self._seq)
        return sum(i[0] * i[1] for i in zip(self._seq, vec))

    @property
    def length(self):
        return math.sqrt(sum([v**2 for v in self._seq]))

    @property
    def x(self):
        return self._seq[0]

    @x.setter
    def x(self, value):
        self._seq[0] = value

    @property
    def y(self):
        return self._seq[1]

    @y.setter
    def y(self, value):
        self._seq[1] = value

    @property
    def z(self):
        if self.length < 3:
            raise AttributeErorr("unavailable on 2d vector")
        return self._seq[2]

    @z.setter
    def z(self, value):
        self._seq[2] = value

    @property
    def xy(self):
        return Vector2(self._seq[:2])

    @xy.setter
    def xy(self, value):
        self.x = value[0]
        self.y = value[1]

    @property
    def yx(self):
        return Vector2(self._seq[1::-1])

    @yx.setter
    def yx(self, value):
        self.y = value[0]
        self.x = value[1]


class Island:
    """ data type for storing connected vertices """
    def __init__(self, coords, island_type="BASIC"):
        assert type(coords) in (tuple, list)
        self._coords = list(coords)
        self._type = island_type

    def __str__(self):
        return "Island of {c} coordinates.".format(c=len(self._coords))

    def __len__(self):
        return len(self._coords)

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self):
        if self._idx < len(self._coords):
            result = self._coords[self._idx]
            self._idx += 1
            return result
        else:
            raise StopIteration

    @property
    def coords(self):
        return self._coords

    @property
    def type(self):
        return self._type

    def append(self, coord):
        assert type(coord) in (tuple, list, Vector, Vector2)
        return self._coords.append(coord)

    def invert_distribution(self):
        self._distribution = [[not val for val in col] for col in self._distribution]

    def print_distribution(self):
        print()
        distribution = self._distribution
        for y in range(len(distribution[0]) - 1, -1, -1):
            for x in range(len(distribution)):
                print("X " if distribution[x][y] else "_ ", end="")
            print()
        print()

    def dilate_erode(self, dist):
        if self.type == "OUTLINE":
            return
        bme = self.to_bmesh()
        mesh_offset(bme, dist)
        self.from_bmesh(bme)

    def transform(self, mx):
        bme = self.to_bmesh(face=False)
        if len(mx[0]) == 3:
            mx = mx_2d_to_3d(mx)
        bmesh.ops.transform(bme, matrix=mx, verts=bme.verts)
        self.from_bmesh(bme)

    def get_insideness_depth(self, archipelago):
        assert self in archipelago.islands
        insideness_depth = 0
        inside_outline = False
        centerpoint = self.get_bounds_info().mid
        for isl in archipelago.islands:
            # don't check against itself
            if isl == self:
                continue
            # do simple point in poly check to rule out most cases
            isl_bounds = get_bounds(isl.coords)
            isl_bounds_2d = [isl_bounds[0], isl_bounds[3], isl_bounds[7], isl_bounds[4]]
            if not pointnpoly(centerpoint, isl_bounds_2d):
                continue
            # do full poly in poly check
            is_inside_isl = polynpoly(self.coords, isl.coords)
            # handle outline as special case
            if isl.type == "OUTLINE":
                inside_outline = is_inside_isl
                if not archipelago.inverted:
                    continue
            # increase island depth
            if is_inside_isl:
                insideness_depth += 1
        return insideness_depth, inside_outline

    def get_bounds_info(self):
        bound_coords = get_bounds(self._coords)

        get_max = lambda i: max([co[i] for co in bound_coords])
        get_min = lambda i: min([co[i] for co in bound_coords])

        info = lambda: None
        info.max = Vector2((get_max(0), get_max(1), get_max(2)))
        info.min = Vector2((get_min(0), get_min(1), get_min(2)))
        info.mid = (info.min + info.max) / 2
        info.dist = info.max - info.min
        return info

    def get_dimensions(self):
        bounds = self.get_bounds()
        bounds_max = bounds[-2]
        bounds_min = bounds[0]
        return Vector2((bounds_max[0] - bounds_min[0], bounds_max[1] - bounds_min[1]))

    def to_bmesh(self, bme=None, face=True):
        bme = bme or bmesh.new()
        verts = list()
        for coord in self._coords:
            v = bme.verts.new(coord)
            if len(verts) > 0:
                bme.edges.new((v, verts[-1]))
            verts.append(v)
        if len(verts) > 1:
            bme.edges.new((verts[-1], verts[0]))
        if face:
            bme.faces.new(verts)
        return bme

    def to_mesh(self, mesh, face=True):
        bme = self.to_bmesh(face=face)
        return bme.to_mesh(mesh)

    def from_bmesh(self, bme):
        self._coords = [Vector2(v.co) for v in bme.verts]

    def draw(self, face=True):
        m = bpy.data.meshes.new(str(self))
        self.to_mesh(m, face=face)
        obj = bpy.data.objects.new(str(self), m)
        link_object(obj)
        return obj


class Archipelago:
    """ data type for storing a group of Islands """
    def __init__(self, islands=None, island_type="BASIC"):
        # initialize empty parameters
        if islands is None:
            islands = []
        # further class initialization
        assert type(islands) in (tuple, list)
        for island in islands:
            assert type(island) in (tuple, list, Island)
        self._islands = list()
        for island in islands:
            self._islands.append(island if isinstance(island, Island) else Island(island, island_type=island_type))

    def __str__(self):
        return "Archipelago of {i} islands with {v} total vertices.".format(i=len(self._islands), v=len(self.coords))

    def __len__(self):
        return len(self._islands)

    def __add__(self, other):
        assert isinstance(other, Archipelago)
        new_arch = Archipelago([island for island in self.islands])
        for island in other.islands:
            new_arch.append(island)
        return new_arch

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self):
        if self._idx < len(self._islands):
            result = self._islands[self._idx]
            self._idx += 1
            return result
        else:
            raise StopIteration

    @property
    def islands(self):
        return self._islands

    @property
    def coords(self):
        all_coords = list()
        for island in self._islands:
            all_coords += island.coords
        return all_coords

    def append(self, island):
        assert type(island) in (tuple, list, Island)
        return self._islands.append(island if isinstance(island, Island) else Island(island))

    def get_outline_island(self):
        return next(isl for isl in self._islands if isl.type == "OUTLINE")

    def dilate_erode(self, dist):
        if self._inverted:
            dist *= -1
        for island in self._islands:
            cur_dist = dist
            if island.get_insideness_depth(self)[0] % 2 == 1:
                cur_dist *= -1
            island.dilate_erode(cur_dist)

    def invert(self):
        self._inverted = not self._inverted

    def transform(self, mx):
        for island in self._islands:
            island.transform(mx)

    def to_mesh(self, mesh, face=True, island_types=None):
        bme = bmesh.new()
        for island in self._islands:
            if island_types is None or island.type in island_types:
                island.to_bmesh(bme, face=face)
        return bme.to_mesh(mesh)

    def draw(self, face=True, island_types=None):
        m = bpy.data.meshes.new(str(self))
        self.to_mesh(m, face, island_types)
        obj = bpy.data.objects.new(str(self), m)
        bpy.context.scene.collection.objects.link(obj)
        return obj


class ArchipelagoSequence:
    """ data type for storing a sequence of Archipelagos """
    def __init__(self, archipelagos=None):
        if archipelagos is None:
            self._archipelagos = list()
            return
        assert type(archipelagos) in (tuple, list)
        self._archipelagos = [a for a in archipelagos if isinstance(a, Archipelago)]

    def __str__(self):
        return "Sequence of {i} Archipelagos.".format(i=len(self._archipelagos))

    def __len__(self):
        return len(self._archipelagos)

    def __add__(self, other):
        assert isinstance(other, ArchipelagoSequence)
        new_arch_seq = Archipelago([a for a in self._archipelagos])
        for arch in other.archipelagos:
            new_arch_seq.append(arch)
        return new_arch_seq

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self):
        if self._idx < len(self._archipelagos):
            result = self._archipelagos[self._idx]
            self._idx += 1
            return result
        else:
            raise StopIteration

    @property
    def archipelagos(self):
        return self._archipelagos

    def append(self, arch):
        assert isinstance(arch, Archipelago)
        return self._archipelagos.append(arch)

    def get_outline_island(self):
        assert len(self._archipelagos) > 0
        return self._archipelagos[0].get_outline_island()

    def dilate_erode(self, dist):
        for archipelago in self._archipelagos:
            archipelago.dilate_erode(dist)

    def invert(self):
        for archipelago in self._archipelagos:
            archipelago.invert()

    def transform(self, mx):
        for archipelago in self._archipelagos:
            archipelago.transform(mx)


class MyImage:
    """ data type for storing and manipulating images with real-world dimensions """
    def __init__(self, pixels, size=(1, 1), name="Image", dimensions=None, channels=None, display_aspect=(1, 1), file_extension=".png"):
        assert size and size[0] > 0 and size[1] > 0
        self._name = name
        self.pixels = pixels
        self.size = size
        self.dimensions = dimensions
        self._display_aspect = display_aspect
        self._channels = channels or len(self.pixels) // (size[0] * size[1])
        assert self._channels and isinstance(self._channels, int) and self._channels in (1, 3, 4)
        self._file_extension = file_extension

    def __str__(self):
        return "<MyImage[{x_size} x {y_size}]>".format(x_size=self._size[0], y_size=self._size[1])

    def __len__(self):
        return len(self._pixels)

    def __iter__(self):
        self._idx = 0
        return self

    def __next__(self):
        if self._idx < len(self._pixels):
            result = list(self._pixels[self._idx:self._idx + self._channels])
            self._idx += self._channels
            return result
        else:
            raise StopIteration

    def copy(self):
        return MyImage(self._pixels.copy(), tuple(self.size), "Copy of " + self.name, dimensions=None if self.dimensions is None else tuple(self.dimensions), channels=self.channels, display_aspect=tuple(self.display_aspect))

    @property
    def name(self):
        return self._name

    @property
    def pixels(self):
        return list(self._pixels)

    @pixels.setter
    def pixels(self, value):
        if type(value) in (tuple, list, Color, bpy.types.bpy_prop_array):
            self._pixels = np.array(value)
        elif isinstance(value, np.ndarray):
            self._pixels = value
        else:
            raise Exception("unsupported type for 'pixels' property")

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if type(value) in (Vector, Vector2, np.ndarray):
            self._size = vec_conv(value, inner_type=int, outer_type=list)
        elif type(value) in (list, tuple, bpy.types.bpy_prop_array):
            self._size = list(value)
        else:
            raise Exception("'size' argument is of unsupported type")

    @property
    def dimensions(self):
        return self._dimensions

    @dimensions.setter
    def dimensions(self, value):
        if value is None:
            self._dimensions = None
        elif type(value) in (list, tuple, Vector, Vector2, np.ndarray, bpy.types.bpy_prop_array):
            self._dimensions = [round(value[0], 6), round(value[1], 6)]
        else:
            raise Exception("'dimensions' argument is of unsupported type")

    @property
    def channels(self):
        return self._channels

    @property
    def display_aspect(self):
        return self._display_aspect

    @property
    def file_extension(self):
        return self._file_extension

    @file_extension.setter
    def file_extension(self, value):
        assert isinstance(value, str)
        self._file_extension = value

    def translate(self, translate_x, translate_y, space="RELATIVE", expand_canvas=False, wrap_x=True, wrap_y=True):
        if not any((translate_x, translate_y)):
            return
        # convert translation values
        if space == "RELATIVE":
            translate_x = round(translate_x * self.size[0])
            translate_y = round(translate_y * self.size[1])
        elif space == "METRIC":
            translate_x = round(translate_x * (self.size[0] / self.dimensions[0]))
            translate_y = round(translate_y * (self.size[1] / self.dimensions[1]))
        elif space == "PIXELS":
            translate_x = round(translate_x)
            translate_y = round(translate_y)
        # expand the canvas if necessary
        if expand_canvas:
            self.pad_to_size(width=self.size[0] + abs(translate_x) * 2, height=self.size[1] + abs(translate_y) * 2)
        # translate the pixels
        old_pixels = self._pixels
        pixels = translate_pixels(old_pixels, translate_x, translate_y, wrap_x, wrap_y, self.size[0], self.size[1], self.channels)
        self.pixels = pixels

    def resize(self, width=None, height=None, preserve_canvas=False):
        """ resize image using nearest neighbor """
        assert width or height
        if width is None:
            width = round(height * self.size[0] / self.size[1])
        if height is None:
            height = round(width * self.size[1] / self.size[0])
        if width == self.size[0] and height == self.size[1]:
            return
        first_idx = np.array((width, height))
        old_pixels = self._pixels
        old_size = np.array(self.size)
        if preserve_canvas:
            pixels = resize_pixels_preserve_borders(first_idx, self._channels, old_pixels, old_size)
        else:
            pixels = resize_pixels(first_idx, self._channels, old_pixels, old_size)
        self.pixels = pixels
        if not preserve_canvas:
            self.dimensions = vec_mult(self.dimensions, first_idx / self.size)
            self.size = first_idx

    def crop(self, width=None, height=None):
        if width is None:
            width = self.size[0]
        if height is None:
            height = self.size[1]
        first_idx = np.array((width, height))
        old_pixels = self._pixels
        old_size = np.array(self.size)
        pixels = crop_pixels(first_idx, self._channels, old_pixels, old_size)
        self.pixels = pixels
        self.size = first_idx

    def pad_to_size(self, width=None, height=None):
        if width is None:
            width = self.size[0]
        if height is None:
            height = self.size[1]
        if width <= self.size[0] and height <= self.size[1]:
            return
        first_idx = np.array((width, height))
        old_pixels = self._pixels
        old_size = np.array(self.size)
        self.pixels = pad_pixels(first_idx, self._channels, old_pixels, old_size)
        self.dimensions = vec_mult(self.dimensions, first_idx / self.size)
        self.size = first_idx

    def write_to_disk(self, directory="//", name=None):
        name = name or self.name
        image = self.make_blend_image(name + "__dup__")
        image_fp = join(directory, name + self.file_extension)
        image.filepath_raw = image_fp
        file_formats = {
            ".png": "PNG",
            ".jpg": "JPEG",
            ".bmp": "BMP",
            ".tga": "TARGA",
        }
        image.file_format = file_formats[self.file_extension]
        image.save()
        bpy.data.images.remove(image)
        return bpy.path.abspath(image_fp)

    def to_hsv(self):
        assert self._channels >= 3
        channels = self.channels
        hsv_pixels = np.empty(self.size[0] * self.size[1] * 3)
        for i in range(len(hsv_pixels) // 3):
            idx1 = i * channels
            idx2 = i * 3
            hsv_pixels[idx2:idx2 + 3] = rgb_to_hsv(self._pixels[idx1], self._pixels[idx1 + 1], self._pixels[idx1 + 2])
        return hsv_pixels

    def from_hsv(self, array, overwrite=True):
        if self._channels != 3:
            self._pixels = np.empty(self.size[0] * self.size[1] * 3)
            self._channels = 3
        for i in range(0, len(array), 3):
            self._pixels[i:i + 3] = hsv_to_rgb(array[i], array[i + 1], array[i + 2])

    # def to_pixels_1d(self):
    #     return get_1d_pixel_array(self._pixels, self._size, self._channels)
    #
    # def to_pixels_2d(self):
    #     """ columns of rows of color values """
    #     return get_2d_pixel_array(self._pixels, self._size, self._channels)
    #
    # def from_pixels_1d(self, array):
    #     self._pixels = np.empty(len(array) * len(array[0]))
    #     for i in range(len(array)):
    #         for j in range(len(array[i])):
    #             self._pixels[i * len(array[0]) + j] = array[i][j]
    #
    # def from_pixels_2d(self, array, overwrite=True):
    #     self._pixels = np.empty(len(array) * len(array[0]) * len(array[0][0]))
    #     pixel_type = type(array[0][0])
    #     if pixel_type in (list, tuple, Vector, np.ndarray, bpy.types.bpy_prop_array):
    #         for col in range(len(array[0])):
    #             for row in range(len(array)):
    #                 self._pixels += list(array[row][col])
    #     elif pixel_type == int:
    #         for col in range(len(array[0])):
    #             for row in range(len(array)):
    #                 self._pixels.append(array[row][col])

    def make_blend_image(self, name=None, overwrite=True):
        name = name or self.name
        im = bpy.data.images.get(name)
        if overwrite and im:
            bpy.data.images.remove(im)
        im = bpy.data.images.new(name=name, alpha=self.channels == 4, width=self.size[0], height=self.size[1])
        im_pix = self._pixels if self.channels == 4 else convert_channels(4, self._pixels, self._channels)
        if im_pix.dtype != np.float32:
            im_pix = im_pix.astype(np.float32)
        set_pixels(im, im_pix)
        return im

    def get_channel(self, channel):
        assert 0 <= channel <= self._channels - 1
        values = [self._pixels[i + channel] for i in range(0, len(self._pixels), self._channels)]
        return MyImage(values, size=self.size, dimensions=self.dimensions, channels=1)

    def set_alpha_channel(self, value):
        old_pixels = self._pixels
        num_pix = self.size[0] * self.size[1]
        assert type(value) in (MyImage, float, int)
        if isinstance(value, MyImage):
            assert value.channels == 1
        alpha_val = value.pixels if isinstance(value, MyImage) else value
        self.pixels = set_alpha_channel(num_pix, old_pixels, self._channels, alpha_val)
        self._channels = 4

    def set_channels(self, value, verbose=False, use_alpha=False):
        # check for edge cases
        if value == self._channels:
            return
        assert value in (1, 3, 4)
        if len(self._pixels) == 0:
            return
        # print status
        if verbose:
            ct = time.time()
            print("converting channels...")
        # add or remove color channel(s) from pixel values
        num_pix = self.size[0] * self.size[1]
        old_pixels = self._pixels
        pixels = convert_channels(value, old_pixels, self._channels, use_alpha=use_alpha)
        # set new pixel values and channels
        self.pixels = pixels
        self._channels = value
        # print status
        if verbose:
            stopwatch("Time elapsed", ct)

    def blend(self, image, blend_type, use_clamp, factor):
        assert self.size == image.size and self.channels == image.channels
        image1_pixels = self._pixels
        image2_pixels = image.images[0]._pixels if isinstance(image, MyImageSequence) else image._pixels
        if isinstance(factor, MyImageSequence):
            factor = factor.images[0]._pixels
        elif isinstance(factor, MyImage):
            factor = factor._pixels

        width, height = self.size
        # ct = time.time()
        self.pixels = blend_pixels(image1_pixels, image2_pixels, width, height, self._channels, blend_type, use_clamp, factor)
        # stopwatch("bend", ct)
        # blend_types = ["MIX", "ADD", "SUBTRACT"]
        # num_pix = width * height * self._channels
        # ct = time.time()
        # stream = cuda.stream()
        # with stream.auto_synchronize():
        #     d_new_pixels = cuda.device_array((num_pix,), stream=stream)
        #     d_image1_pixels = cuda.to_device(image1_pixels, stream=stream)
        #     d_image2_pixels = cuda.to_device(image2_pixels, stream=stream)
        #     # ct = stopwatch("b1", ct)
        #     blend_pixels_cuda[get_gpu_info(num_pix, stream=stream)](d_new_pixels, d_image1_pixels, d_image2_pixels, width, height, blend_types.index(blend_type), use_clamp, factor)
        #     # ct = stopwatch("b2", ct)
        #     new_pixels = d_new_pixels.copy_to_host(stream=stream)
        #     # ct = stopwatch("b3", ct)
        # ct = stopwatch("b4", ct)
        # self.pixels = new_pixels

    def clamp(self, minimum=0, maximum=1):
        self.pixels = clamp_pixels(self._pixels, minimum, maximum)

    def normalize(self):
        self.pixels = normalize_pixels(self._pixels)

    def math_operation(self, operation, value, clamp=False):
        self.pixels = math_operation_on_pixels(self._pixels, operation, value, clamp)

    def adjust_bright_contrast(self, bright=0, contrast=0):
        self.pixels = adjust_bright_contrast(self._pixels, bright, contrast)
        # adjust_bright_contrast_cuda[get_gpu_info(pixels.size)](pixels, bright, contrast)
        # self.pixels = pixels

    def adjust_hue_saturation_value(self, hue=0.5, saturation=1, value=1):
        hsv_pixels = np.array(self.to_hsv())
        adjusted_hsv_pixels = adjust_hue_saturation_value(hsv_pixels, hue, saturation, value, channels=3)
        self.from_hsv(adjusted_hsv_pixels)

    def invert(self, factor=1):
        self.pixels = invert_pixels(self._pixels, factor, channels=self._channels)

    def ramp_color(self, color_ramp):
        self.set_channels(1)
        self.pixels = ramp_color(self._pixels, self.size[0], self.size[1], color_ramp.elements)
        self._channels = 4

    def blur(self, radius, filter_type="FLAT", expand_canvas=False):
        if expand_canvas:
            self.pad_to_size(width=self.size[0] + radius[0] * 4, height=self.size[1] + radius[1] * 4)
        self.pixels = blur_pixels(self._pixels, self.size[0], self.size[1], channels=self._channels, blur_radius=radius, filter_type=filter_type)

    def dilate(self, pixel_dist:tuple, threshold:float, mode:str="STEP"):  # method: STEP, DISTANCE
        self.set_channels(1)
        if not any(pixel_dist):
            return
        old_pixels = self._pixels
        pixel_dist = np.array((pixel_dist[0], pixel_dist[1]))
        if mode == "STEP":
            new_pixels = dilate_pixels_step(old_pixels, pixel_dist, self.size[0], self.size[1])
        else:
            new_pixels = dilate_pixels_dist(old_pixels, pixel_dist, self.size[0], self.size[1])
        # ct = time.time()
        # stream = cuda.stream()
        # with stream.auto_synchronize():
        #     d_new_pixels = cuda.device_array((old_pixels.size,), stream=stream)
        #     d_old_pixels = cuda.to_device(old_pixels, stream=stream)
        #     ct = stopwatch("d1", ct)
        #     dilate_pixels_cuda[get_gpu_info(old_pixels.size, stream=stream)](d_new_pixels, d_old_pixels, pixel_dist, 1 if mode == "DISTANCE" else 0, self.size[0], self.size[1])
        #     ct = stopwatch("d2", ct)
        #     new_pixels = d_new_pixels.copy_to_host(stream=stream)
        #     ct = stopwatch("d3", ct)
        # ct = stopwatch("d4", ct)
        self.pixels = new_pixels

    def flip(self, flip_x=True, flip_y=True):
        if not any((flip_x, flip_y)):
            return
        old_pixels = self._pixels
        pixels = flip_pixels(old_pixels, flip_x, flip_y, self.size[0], self.size[1], self.channels)
        self.pixels = pixels


class MyImageSequence:
    """ data type for storing and manipulating sequences of MyImages """
    def __init__(self, images, offset=0, name="Image Sequence"):
        assert type(images) in (list, tuple)
        self._name = name
        self.images = images
        self.offset = offset

    def copy(self):
        new_images = list()
        for im in self.images:
            new_images.append(im.copy())
        return MyImageSequence(new_images, self.offset, "Copy of " + self.name)

    @property
    def name(self):
        return self._name

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, value):
        assert type(value) in (list, tuple)
        self._images = value

    @property
    def frame_duration(self):
        return len(self._images)

    @property
    def channels(self):
        assert len(self.images) > 0
        return self.images[0].channels

    @property
    def dimensions(self):
        assert len(self.images) > 0
        return self.images[0].dimensions

    @dimensions.setter
    def dimensions(self, value):
        for im in self.images:
            im.dimensions = value

    @property
    def size(self):
        assert len(self.images) > 0
        return self.images[0].size

    @size.setter
    def size(self, value):
        for im in self.images:
            im.size = value

    @property
    def file_extension(self):
        assert len(self.images) > 0
        return self.images[0].file_extension

    @file_extension.setter
    def file_extension(self, value):
        for im in self.images:
            im.file_extension = value

    def translate(self, translate_x, translate_y, use_relative=False, expand_canvas=False, wrap_x=True, wrap_y=True):
        for im in self.images:
            im.translate(translate_x, translate_y, use_relative, expand_canvas, wrap_x, wrap_y)

    def resize(self, width=None, height=None, preserve_canvas=False):
        for im in self.images:
            im.resize(width, height, preserve_canvas)

    def crop(self, width=None, height=None):
        for im in self.images:
            im.crop(width, height)

    def pad_to_size(self, width=None, height=None):
        for im in self.images:
            im.pad_to_size(width, height)

    def write_to_disk(self, directory="//"):
        image_filepaths = list()
        for j, im in enumerate(self.images):
            im_name = self.name + "_{num}".format(num=str(j + 1).zfill(4))
            image_fp = im.write_to_disk(directory, name=im_name)
            image_filepaths.append(image_fp)
        return image_filepaths

    def make_blend_image(self, name=None, directory=None, overwrite=True):
        assert len(self.images) > 0
        directory = directory or temp_path()
        image_fps = self.write_to_disk(directory=directory)
        im_seq = bpy.data.images.load(image_fps[0])
        im_seq.source = "SEQUENCE"
        return im_seq

    def get_channel(self, channel):
        new_images = list()
        for im in self.images:
            new_images.append(im.get_channel(channel))
        return MyImageSequence(new_images, self.offset)

    def set_alpha_channel(self, value):
        if isinstance(value, MyImageSequence):
            assert self.frame_duration == value.frame_duration
        for j, im in enumerate(self.images):
            alpha_val = value.images[j] if isinstance(value, MyImageSequence) else value
            im.set_alpha_channel(alpha_val)

    def set_channels(self, value, verbose=False):
        # check for edge cases
        if value == self.channels:
            return
        assert value in (1, 3, 4)
        if len(self.images) == 0 or len(self.images[0].pixels) == 0:
            return
        # print status
        if verbose:
            ct = time.time()
            print("converting channels...")
        # set channels for each image
        for im in self.images:
            im.set_channels(value)
        # print status
        if verbose:
            stopwatch("Time elapsed", ct)

    def blend(self, image, blend_type, use_clamp, factor):
        for im in self.images:
            im.blend(image, blend_type, use_clamp, factor)

    def clamp(self, minimum=0, maximum=1):
        for im in self.images:
            im.clamp(im, minimum, maximum)

    def normalize(self):
        for im in self.images:
            im.normalize(im)

    def math_operation(self, operation, value, clamp=False):
        for im in self.images:
            im.math_operation(im, operation, value, clamp)

    def adjust_bright_contrast(self, bright=0, contrast=0):
        for im in self.images:
            im.adjust_bright_contrast(bright, contrast)

    def adjust_hue_saturation_value(self, hue=0.5, saturation=1, value=1):
        for im in self.images:
            im.adjust_hue_saturation_value(hue, saturation, value)

    def invert(self, factor=1):
        for im in self.images:
            im.invert(factor)

    def blur(self, radius, filter_type="FLAT", expand_canvas=False):
        for im in self.images:
            im.blur(radius, filter_type, expand_canvas)

    def dilate(self, pixel_dist:tuple, threshold:float, mode:str="STEP"):
        for im in self.images:
            im.dilate(pixel_dist, threshold, mode)

    def flip(self, flip_x=True, flip_y=True):
        for im in self.images:
            im.flip(flip_x, flip_y)
