# Copyright (C) 2020 Christopher Gearhart
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
import numpy as np
import time

# Blender imports
import bpy
from bpy.types import Scene, Object, Mesh, Image
from mathutils import Vector
from mathutils.interpolate import poly_3d_calc

# Module imports
from .colors import *
from .materials import *
from .maths import *
from .reporting import *
from .wrappers import *

common_pixel_cache = dict()


@blender_version_wrapper("<=","2.82")
def get_pixels(image:Image, color_depth=-1):
    pixels = np.array(image.pixels[:])
    if color_depth >= 0:
        pixels = cluster_pixels(pixels, color_depth, image.channels)
    return pixels
@blender_version_wrapper(">=","2.83")
def get_pixels(image:Image, color_depth=-1):
    pixels = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(pixels)
    if color_depth >= 0:
        pixels = cluster_pixels(pixels, color_depth, image.channels)
    return pixels


@blender_version_wrapper("<=","2.82")
def set_pixels(image:Image, pix:list):
    image.pixels = pix
@blender_version_wrapper(">=","2.83")
def set_pixels(image:Image, pix:list):
    image.pixels.foreach_set(pix)


def get_pixels_cache(image:Image, frame:int=None, color_depth:int=-1):
    """ get pixels from image (cached by image name (and frame if movie/sequence); make copy of result if modifying) """
    scn = bpy.context.scene
    frame = scn.frame_current if frame is None else frame
    image_key = image.name if image.source == "FILE" else ("{im_name}_f_{frame}".format(im_name=image.name, frame=frame))
    if color_depth != -1:
         image_key += "_depth_{}".format(color_depth)

    if image_key not in common_pixel_cache or len(common_pixel_cache[image_key]) == 0:
        pixels = get_pixels(image, color_depth=color_depth) if image.source in ("FILE", "GENERATED") else get_pixels_at_frame(image, frame)
        common_pixel_cache[image_key] = pixels
    return common_pixel_cache[image_key]


def clear_pixel_cache(image_name:str=None):
    """ clear the pixel cache """
    if image_name is None:
        common_pixel_cache = dict()
    else:
        for key in common_pixel_cache.keys():
            if key.startswith(image_name):
                common_pixel_cache.pop(key)


def get_pixels_at_frame(image:Image, frame:int=None, cyclic:bool=True):
    assert image.source in ("SEQUENCE", "MOVIE")
    frame = frame or bpy.context.scene.frame_current
    old_viewer_area = ""
    viewer_area = None
    viewer_space = None

    assert bpy.context.screen is not None
    viewer_area = next((area for area in bpy.context.screen.areas if area.type == "IMAGE_EDITOR"), None)
    if viewer_area is None:
        viewer_area = bpy.context.screen.areas[0]
        old_viewer_area = viewer_area.type
        viewer_area.type = "IMAGE_EDITOR"

    assert viewer_area is not None
    viewer_space = next(space for space in viewer_area.spaces if space.type == "IMAGE_EDITOR")

    old_image = viewer_space.image
    viewer_space.image = image
    viewer_space.image_user.frame_offset = frame - (bpy.context.scene.frame_current % image.frame_duration)
    viewer_space.image_user.use_cyclic = cyclic
    if image.source == "MOVIE" and viewer_space.image_user.frame_duration != image.frame_duration:
        viewer_space.image_user.frame_duration = image.frame_duration
    elif image.source == "SEQUENCE":
        viewer_space.image_user.frame_duration = frame + 1
    viewer_space.display_channels = "COLOR"  # force refresh of image pixels
    pixels = get_pixels(viewer_space.image)

    if old_viewer_area != "":
        viewer_area.type = old_viewer_area
    else:
        viewer_space.image = old_image

    return pixels


# reference: https://svn.blender.org/svnroot/bf-extensions/trunk/py/scripts/addons/uv_bake_texture_to_vcols.py
def get_pixel(image:Image, uv_coord:Vector, premult:bool=False, pixels:list=None, image_frame:int=None, color_depth:int=-1):
    """ get RGBA value for specified coordinate in UV image
    image       -- blend image holding the pixel data
    uv_coord    -- UV coordinate of desired pixel value
    premult     -- premultiply the alpha channel of the image
    pixels      -- list of pixel data from UV texture image
    image_frame -- frame from image to get pixel values from (defaults to scn.frame_current)
    color_depth -- number of colors in the image in the power of 2 (see 'median_cut_clustering.py')
    """
    pixels = pixels or get_pixels_cache(image, frame=image_frame, color_depth=color_depth)
    pixel_number = (image.size[0] * round(uv_coord.y) + round(uv_coord.x)) * image.channels
    assert 0 <= pixel_number < len(pixels)
    rgba = pixels[pixel_number:pixel_number + image.channels]
    # premultiply
    if premult and image.alpha_mode != "PREMUL":
        rgba = [v * rgba[3] for v in rgba[:3]] + [rgba[3]]
    # un-premultiply
    elif not premult and image.alpha_mode == "PREMUL":
        if rgba[3] == 0:
            rgba = [0] * 4
        else:
            rgba = [v / rgba[3] for v in rgba[:3]] + [rgba[3]]
    return rgba


def get_uv_pixel_color(obj:Object, face_idx:int, point:Vector, uv_image:Image=None, image_frame:int=None, mapping_loc:Vector=Vector((0, 0)), mapping_scale:Vector=Vector((1, 1)), color_depth:int=-1):
    """ get RGBA value in UV image for point at specified face index """
    if face_idx is None:
        return None
    # get uv_layer image for face
    image = get_uv_image(obj, face_idx, uv_image)
    if image is None:
        return None
    # get uv coordinate based on nearest face intersection
    uv_coord = get_uv_coord(obj, face_idx, point, image, mapping_loc, mapping_scale)
    # retrieve rgba value at uv coordinate
    rgba = get_pixel(image, uv_coord, image_frame=image_frame, color_depth=color_depth)
    # gamma correct color value
    if image.colorspace_settings.name == "sRGB":
        rgba = gamma_correct_srgb_to_linear(rgba)
    return [round(v, 6) for v in rgba]


def get_uv_image(obj:Object, face_idx:int, uv_image:Image=None):
    """ returns UV image for object (priority to passed image, then face index, then first one found in material nodes) """
    image = verify_img(uv_image)
    # TODO: Reinstate this functionality for b280()
    if not b280() and image is None and obj.data.uv_textures.active:
        image = verify_img(obj.data.uv_textures.active.data[face_idx].image)
    if image is None:
        try:
            mat_idx = obj.data.polygons[face_idx].material_index
            image = get_first_img_from_nodes(obj, mat_idx)
        except IndexError:
            mat_idx = 0
            while image is None and mat_idx < len(obj.material_slots):
                image = get_first_img_from_nodes(obj, mat_idx)
                mat_idx += 1
    return image


def get_first_img_from_nodes(obj:Object, mat_slot_idx:int):
    """ return first image texture found in a material slot """
    mat = obj.material_slots[mat_slot_idx].material
    if mat is None or not mat.use_nodes:
        return None
    nodes_to_check = list(mat.node_tree.nodes)
    active_node = mat.node_tree.nodes.active
    if active_node is not None: nodes_to_check.insert(0, active_node)
    img = None
    for node in nodes_to_check:
        if node.type != "TEX_IMAGE" or node.mute:
            continue
        elif len([o for o in node.outputs if o.is_linked]) == 0:
            continue
        img = verify_img(node.image)
        if img is not None:
            break
    return img


def verify_img(im:Image):
    """ verify image has pixel data """
    if not im:
        return None
    if not im.has_data:
        try:
            im.update()
        except RuntimeError:
            pass
    return im if im is not None and im.pixels is not None and len(im.pixels) > 0 else None


def duplicate_image(img:Image, name:str, new_pixels:np.ndarray=None):
    width, height = img.size
    new_image = bpy.data.images.new(name, width, height)
    new_pixels = new_pixels if new_pixels is not None else get_pixels(img)
    set_pixels(new_image, new_pixels)
    return new_image


@timed_call("test", precision=6)
def get_uv_coord(obj:Object, face_idx:int, point:Vector, image:Image, mapping_loc:Vector=Vector((0, 0)), mapping_scale:Vector=Vector((1, 1))):
    """ returns UV coordinate of target point in source mesh image texture
    mesh          -- source object containing mesh data
    face          -- index of face from mesh
    point         -- coordinate of target point on source mesh
    image         -- image texture for source mesh
    mapping_loc   -- offset uv coord location (from mapping node)
    mapping_scale -- offset uv coord scale (from mapping node)
    """
    # get active uv layer data
    mat = get_mat_at_face_idx(obj, face_idx)
    uv = get_uv_layer_data(obj, mat)
    # get face from face index
    face = obj.data.polygons[face_idx]
    # get 3D coordinates of face's vertices
    lco = [obj.data.vertices[i].co for i in face.vertices]
    # get uv coordinates of face's vertices
    luv = [uv[i].uv for i in face.loop_indices]
    # calculate barycentric weights for point
    lwts = poly_3d_calc(lco, point)
    # multiply barycentric weights by uv coordinates
    uv_loc = sum((p*w for p,w in zip(luv,lwts)), Vector((0,0)))
    # ensure uv_loc is in range(0,1)
    uv_loc = Vector((round(uv_loc[0], 5) % 1, round(uv_loc[1], 5) % 1))
    # apply location and scale offset
    uv_loc = vec_div(uv_loc - mapping_loc, mapping_scale)
    # once again ensure uv_loc is in range(0,1)
    uv_loc = Vector((round(uv_loc[0], 5) % 1, round(uv_loc[1], 5) % 1))
    # convert uv_loc in range(0,1) to uv coordinate
    image_size_x, image_size_y = image.size
    x_co = round(uv_loc.x * (image_size_x - 1))
    y_co = round(uv_loc.y * (image_size_y - 1))
    uv_coord = (x_co, y_co)

    # return resulting uv coordinate
    return Vector(uv_coord)


def get_uv_coord_in_ref_image(loc:Vector, img_obj:Object):
    """ returns UV coordinate of target 2d point in a reference image object
    point   -- 2d sample location
    img_obj -- reference image to sample
    """
    img_size = Vector(img_obj.data.size)
    img_off = Vector(img_obj.empty_image_offset)
    obj_dimensions = Vector((
        img_obj.empty_display_size,
        img_obj.empty_display_size * img_size.y / img_size.x,
    ))
    obj_dimensions = vec_mult(obj_dimensions, img_obj.scale)
    relative_loc = loc.xy - img_obj.location.xy
    pixel_offset = Vector((
        relative_loc.x * (img_size.x / obj_dimensions.x),
        relative_loc.y * (img_size.y / obj_dimensions.y),
    ))
    pixel_loc = Vector(pixel_offset[:2]) - vec_mult(img_size, img_off)
    return pixel_loc


def get_uv_layer_data(obj, mat=None):
    """ returns data of active uv texture for object """
    obj_uv_layers = obj.data.uv_layers if b280() else obj.data.uv_textures
    # get uv layer from node in material's node tree
    if mat is not None and mat.use_nodes:
        mat_nodes = mat.node_tree.nodes
        uv_name_from_node = next((node.uv_map for node in mat_nodes if node.type == "UVMAP"), None)
        if uv_name_from_node is not None and uv_name_from_node in obj_uv_layers:
            return obj_uv_layers[uv_name_from_node].data
    # otherwise, get active uv layer
    if len(obj_uv_layers) == 0:
        return None
    active_uv = obj_uv_layers.active
    if active_uv is None:
        obj_uv_layers.active = obj_uv_layers[0]
        active_uv = obj_uv_layers.active
    return active_uv.data


def get_2d_pixel_array(pixels:np.ndarray, channels:int):
    """ converts 1d pixel array to 2d array

    i.e. for a square image with 4 pixels:
    pixels = [
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
    ]
    """
    pixels_2d = np.reshape(pixels, (len(pixels) // channels, channels))
    return pixels_2d


def get_3d_pixel_array(pixels:np.ndarray, height:int, width:int, channels:int):
    """ converts 1d pixel array to 3d array

    i.e. for a square image with 4 pixels:
    pixels = [
        [[1, 1, 1, 1], [1, 1, 1, 1]],
        [[1, 1, 1, 1], [1, 1, 1, 1]],
    ]
    """
    pixels_3d = np.reshape(pixels, (height, width, channels))
    return pixels_3d

def get_1d_pixel_array(array:np.ndarray):
    """ convert pixel array to 1d from 2d or 3d array """
    assert 2 <= len(array.shape) <= 3
    pixels_1d = np.reshape(array, np.prod(array.shape))
    return pixels_1d


def update_empty_image(image:Image):
    assert bpy.context.area is not None
    last_ui_type = bpy.context.area.ui_type
    bpy.context.area.ui_type = "UV"
    bpy.context.area.spaces[0].image = image
    bpy.context.area.ui_type = last_ui_type


#######################################################
#########     MEDIAN CUT CLUSTERING      ##############
#######################################################


def cluster_pixels(pix_1d, depth, channels):
    pix_2d = get_2d_pixel_array(pix_1d, channels)
    new_pix_2d = np.empty(pix_2d.shape, dtype=np.float32)

    new_shape = (len(pix_2d), channels + 1)
    pix_2d_with_idxs = np.empty(new_shape, dtype=np.float32)
    pix_2d_with_idxs[:, :-1] = pix_2d
    pix_2d_with_idxs[:, -1:] = np.arange(len(pix_2d), dtype=np.int64).reshape((len(pix_2d), 1))

    split_into_buckets(new_pix_2d, pix_2d_with_idxs, depth, channels)

    new_pix_1d = new_pix_2d.reshape(len(pix_1d))
    return new_pix_1d


# Adapted and improved from: https://muthu.co/reducing-the-number-of-colors-of-an-image-using-median-cut-algorithm/
def median_cut_quantize(new_img_arr, img_arr, channels):
    # when it reaches the end, color quantize
    # print("to quantize: ", len(img_arr))
    color_ave = list()
    for i in range(channels):
        color_ave.append(np.mean(img_arr[:,i]))

    ind_arr = np.empty((len(img_arr), channels), dtype=np.int64)
    ind_arr_base = img_arr[:,-1] * channels
    for i in range(channels):
        ind_arr[:,i] = ind_arr_base + i
    np.put(new_img_arr, ind_arr, color_ave)


def split_into_buckets(new_img_arr, img_arr, depth=4, channels=3):
    """ Use Median Cut clustering to reduce image color palette to (2^depth) colors

    Parameters:
        new_img_arr  - Empty array with the target 2d pixel array size
        new_img_arr  - Array containing original pixel data (with an extra value in each pixel list containing its target index in new_img_arr)
        depth        – Represents how many colors are needed in the power of 2 (i.e. Depth of 4 means 2^4 = 16 colors)

    Returns:
        None (the array passed to 'new_img_arr' will contain the resulting pixels)
    """

    if len(img_arr) == 0:
        return

    if depth == 0:
        median_cut_quantize(new_img_arr, img_arr, channels)
        return

    assert isinstance(depth, int)

    ct = time.time()
    ranges = []
    for i in range(channels):
        channel_vals = img_arr[:,i]
        ranges.append(np.max(channel_vals) - np.min(channel_vals))
    # ct = stopwatch("1---", ct)

    space_with_highest_range = ranges.index(max(ranges))
    # print("space_with_highest_range:", space_with_highest_range)
    # sort the image pixels by color space with highest range
    ct = time.time()
    img_arr = img_arr[img_arr[:,space_with_highest_range].argsort()]
    # ct = stopwatch("2-------", ct)
    # find the median to divide the array.
    median_index = (len(img_arr) + 1) // 2
    # print("median_index:", median_index)

    #split the array into two buckets along the median
    split_into_buckets(new_img_arr, img_arr[:median_index], depth - 1, channels)
    split_into_buckets(new_img_arr, img_arr[median_index:], depth - 1, channels)
