# Author: Christopher Gearhart

# System imports
import numpy as np
from colorsys import rgb_to_hsv, hsv_to_rgb
try:
    from scipy import signal
    from scipy import ndimage
except ModuleNotFoundError:
    pass
    # print("'scipy' python module not installed")

# Blender imports
# NONE!

# Module imports
from .pixel_effects_reshape import *
from .pixel_effects_median_cut import *
from ..maths import *
# try:
#     from .pixel_effects_numba import *
# except ModuleNotFoundError:
#     print("'numba' python module not installed")


def initialize_gradient_texture(width, height, quadratic=False, orientation="VERTICAL"):
    pixels = np.empty((height, width))
    if orientation == "VERTICAL":
        for row in range(height):
            val = 1 - (height - 1 - row) / (height - 1)
            if quadratic:
                val = val ** 0.5
            pixels[row, :] = val
    else:
        for col in range(width):
            val = 1 - (width - 1 - col) / (width - 1)
            if quadratic:
                val = val ** 0.5
            pixels[:, col] = val
    pixels = get_1d_pixel_array(pixels)
    return pixels


def convert_channels(channels, old_pixels, old_channels, use_alpha=False):
    assert channels != old_channels
    old_pixels = get_2d_pixel_array(old_pixels, old_channels)
    new_pixels = np.empty((len(old_pixels), channels))
    if channels > old_channels:
        if old_channels == 1:
            for i in range(channels):
                new_pixels[:, i] = old_pixels[:, 0]
        elif old_channels == 3:
            new_pixels[:, :3] = old_pixels[:, :3]
            new_pixels[:, 3] = 1
    elif channels < old_channels:
        if channels == 1 and old_channels == 4 and use_alpha:
            new_pixels[:, 0] = old_pixels[:, 3]
        elif channels == 1:
            new_pixels[:, 0] = 0.2126 * old_pixels[:, 0] + 0.7152 * old_pixels[:, 1] + 0.0722 * old_pixels[:, 2]
        elif channels == 3:
            new_pxiels[:, :3] = old_pixels[:, :3]
    new_pixels = get_1d_pixel_array(new_pixels)
    return new_pixels


def set_alpha_channel(num_pix, old_pixels, old_channels, value):
    old_pixels = get_2d_pixel_array(old_pixels, old_channels)
    new_pixels = np.empty((num_pix, 4))
    new_pixels[:, :3] = old_pixels[:, :3]
    new_pixels[:, 3] = value
    new_pixels = get_1d_pixel_array(new_pixels)
    return new_pixels


def crop_pixels(size, channels, old_pixels, old_size):
    old_pixels = get_3d_pixel_array(old_pixels, old_size[1], old_size[0], channels)
    offset_col = (old_size[0] - size[0]) // 2
    offset_row = (old_size[1] - size[1]) // 2
    new_pixels = old_pixels[offset_row:offset_row + size[1], offset_col:offset_col + size[0]]
    new_pixels = get_1d_pixel_array(new_pixels)
    return new_pixels


def pad_pixels(size, channels, old_pixels, old_size):
    new_pixels = np.zeros((size[1], size[0], channels))
    offset_col = (size[0] - old_size[0]) // 2
    offset_row = (size[1] - old_size[1]) // 2
    new_pixels[offset_row:offset_row + old_size[1], offset_col:offset_col + old_size[0]] = old_pixels[:, :]
    new_pixels = get_1d_pixel_array(new_pixels)
    return new_pixels


def blend_pixels(im1_pixels, im2_pixels, width, height, channels, operation, use_clamp, factor):
    new_pixels = np.empty((width * height, channels))
    im1_pixels = get_2d_pixel_array(im1_pixels, channels)
    im2_pixels = get_2d_pixel_array(im2_pixels, channels)
    if isinstance(factor, np.ndarray):
        new_factor = np.empty((len(factor), channels))
        for i in range(channels):
            new_factor[:, i] = factor
        factor = new_factor
    if operation == "MIX":
        new_pixels = im1_pixels * (1 - factor) + im2_pixels * factor
    elif operation == "ADD":
        new_pixels = im1_pixels + im2_pixels * factor
    elif operation == "SUBTRACT":
        new_pixels = im1_pixels - im2_pixels * factor
    elif operation == "MULTIPLY":
        new_pixels = im1_pixels * ((1 - factor) + im2_pixels * factor)
    elif operation == "DIVIDE":
        new_pixels = im1_pixels / ((1 - factor) + im2_pixels * factor)
    elif operation == "POWER":
        new_pixels = im1_pixels ** ((1 - factor) + im2_pixels * factor)
    # elif operation == "LOGARITHM":
    #     new_pixels = math.log(im1_pixels, im2_pixels)
    elif operation == "SQUARE ROOT":
        new_pixels = np.sqrt(im1_pixels)
    elif operation == "ABSOLUTE":
        new_pixels = abs(im1_pixels)
    elif operation == "MINIMUM":
        new_pixels = np.clip(im1_pixels, a_min=im2_pixels, a_max=im1_pixels)
    elif operation == "MAXIMUM":
        new_pixels = np.clip(im1_pixels, a_min=im1_pixels, a_max=im2_pixels)
    elif operation == "LESS THAN":
        new_pixels = (im1_pixels < im2_pixels).astype(int)
    elif operation == "GREATER THAN":
        new_pixels = (im1_pixels > im2_pixels).astype(int)
    elif operation == "ROUND":
        new_pixels = np.round(im1_pixels)
    elif operation == "FLOOR":
        new_pixels = np.floor(im1_pixels)
    elif operation == "CEIL":
        new_pixels = np.ceil(im1_pixels)
    # elif operation == "FRACT":
    #     new_pixels =
    elif operation == "MODULO":
        new_pixels = im1_pixels % im2_pixels

    new_pixels = get_1d_pixel_array(new_pixels)
    if use_clamp:
        np.clip(new_pixels, 0, 1, new_pixels)

    return new_pixels


def math_operation_on_pixels(pixels, operation, value, clamp=False):
    new_pixels = np.empty(pixels.size)
    if operation == "ADD":
        new_pixels = pixels + value
    elif operation == "SUBTRACT":
        new_pixels = pixels - value
    elif operation == "MULTIPLY":
        new_pixels = pixels * value
    elif operation == "DIVIDE":
        new_pixels = pixels / value
    elif operation == "POWER":
        new_pixels = pixels ** value
    # elif operation == "LOGARITHM":
    #     for i in range(new_pixels.size):
    #         new_pixels = math.log(pixels, value)
    elif operation == "SQUARE ROOT":
        new_pixels = np.sqrt(pixels)
    elif operation == "ABSOLUTE":
        new_pixels = abs(pixels)
    elif operation == "MINIMUM":
        new_pixels = np.clip(pixels, a_min=value, a_max=pixels)
    elif operation == "MAXIMUM":
        new_pixels = np.clip(pixels, a_min=pixels, a_max=value)
    elif operation == "LESS THAN":
        new_pixels = (pixels < value).astype(int)
    elif operation == "GREATER THAN":
        new_pixels = (pixels > value).astype(int)
    elif operation == "ROUND":
        new_pixels = np.round(pixels)
    elif operation == "FLOOR":
        new_pixels = np.floor(pixels)
    elif operation == "CEIL":
        new_pixels = np.ceil(pixels)
    # elif operation == "FRACT":
    #     new_pixels =
    elif operation == "MODULO":
        new_pixels = pixels % value
    elif operation == "SINE":
        new_pixels = np.sin(pixels)
    elif operation == "COSINE":
        new_pixels = np.cos(pixels)
    elif operation == "TANGENT":
        new_pixels = np.tan(pixels)
    elif operation == "ARCSINE":
        new_pixels = np.arcsin(pixels)
    elif operation == "ARCCOSINE":
        new_pixels = np.arccos(pixels)
    elif operation == "ARCTANGENT":
        new_pixels = np.arctan(pixels)
    elif operation == "ARCTAN2":
        new_pixels = np.arctan2(pixels)  #, value)

    if clamp:
        np.clip(new_pixels, 0, 1, new_pixels)

    return new_pixels


def clamp_pixels(pixels, minimum, maximum):
    return np.clip(pixels, minimum, maximum)


def normalize_pixels(pixels, to_sum=False):
    new_pixels = np.copy(pixels)
    new_pixels -= np.min(new_pixels, axis=0)
    new_pixels /= (np.sum(new_pixels, axis=0) if to_sum else np.ptp(new_pixels, axis=0))
    return new_pixels


def adjust_bright_contrast(pixels, bright, contrast):
    return contrast * (pixels - 0.5) + 0.5 + bright


def adjust_hue_saturation_value(pixels, hue, saturation, value, channels=3):
    assert channels in (3, 4)
    pixels = get_2d_pixel_array(pixels, channels)
    hue_adjust = hue - 0.5
    pixels[:, 0] = (pixels[:, 0] + hue_adjust) % 1
    pixels[:, 1] = pixels[:, 1] * saturation
    pixels[:, 2] = pixels[:, 2] * value
    return pixels


def invert_pixels(pixels, factor, channels):
    pixels = get_2d_pixel_array(pixels, channels)
    inverted_factor = 1 - factor
    if channels == 4:
        pixels[:, :3] = (inverted_factor * pixels[:, :3]) + (factor * (1 - pixels[:, :3]))
    else:
        pixels = (inverted_factor * pixels) + (factor * (1 - pixels))
    pixels = get_1d_pixel_array(pixels)
    return pixels


def linear_interp(x, y, val):
    return x * val + y * (1 - val)


def ramp_color(old_pixels, width, height, elements):
    pixels = np.empty((height, width, 4))
    for idx in range(4):
        # define cond and func lists for piecewise function
        condlist = [old_pixels < elements[0].position, old_pixels >= elements[-1].position]
        funclist = [lambda x: elements[0].color[idx], lambda x: elements[-1].color[idx]]
        for i in range(len(elements) - 1):
            el1, el2 = elements[i], elements[i + 1]
            condlist.append(np.logical_and(old_pixels >= el1.position, old_pixels < el2.position))
            funclist.append(lambda x, color1=el1.color, color2=el2.color, pos1=el1.position, pos2=el2.position: linear_interp(color2[idx], color1[idx], (x - pos1) / (pos2 - pos1)))
        # execute piecewise function for current index
        pixels[:, :, idx] = np.piecewise(old_pixels, condlist, funclist).reshape((height, width))
    pixels = get_1d_pixel_array(pixels)
    return pixels


def blur_pixels(old_pixels, width, height, channels, blur_radius=1, filter_type="FLAT"):
    old_pixels = get_3d_pixel_array(old_pixels, height, width, channels)
    new_pixels = old_pixels.copy()
    # get 2d blur radius
    assert type(blur_radius) in (int, tuple, list)
    blur_radius_2d = (blur_radius, blur_radius) if isinstance(blur_radius, int) else blur_radius
    # apply blur filter
    if filter_type == "FLAT":
        # get kernel
        kernel_size = (1 + (blur_radius_2d[1] * 2), 1 + (blur_radius_2d[0] * 2))
        kernel = np.ones(kernel_size)
        # run convolve2d to blur pixels
        for i in range(channels):
            neighbor_sum = signal.convolve2d(old_pixels[:, :, i], kernel, mode="same", boundary="fill", fillvalue=0)
            num_neighbor = signal.convolve2d(np.ones((height, width)), kernel, mode="same", boundary="fill", fillvalue=0)
            new_pixels[:, :, i] = neighbor_sum / num_neighbor
    elif filter_type == "GAUSS":
        sigma_2d = (blur_radius_2d[1] / 2, blur_radius_2d[0] / 2)
        for i in range(channels):
            result = ndimage.filters.gaussian_filter(old_pixels[:, :, i], sigma=sigma_2d)
            new_pixels[:, :, i] = result
    # reshape back to 1d aray and return
    new_pixels = get_1d_pixel_array(new_pixels)
    return new_pixels


def flip_pixels(old_pixels, flip_x, flip_y, width, height, channels):
    old_pixels = get_3d_pixel_array(old_pixels, height, width, channels)
    if flix_x and not flip_y:
        new_pixels = old_pixels[:, ::-1]
    elif not flix_x and flip_y:
        new_pixels = old_pixels[::-1, :]
    elif flix_x and flip_y:
        new_pixels = old_pixels[::-1, ::-1]
    new_pixels = get_1d_pixel_array(new_pixels)
    return new_pixels


def translate_pixels(old_pixels, translate_x, translate_y, wrap_x, wrap_y, width, height, channels):
    new_pixels = np.empty((height, width, channels))
    # reshape
    old_pixels = get_3d_pixel_array(old_pixels, width, height, channels)
    # translate x
    if translate_x > 0 or (wrap_x and translate_x != 0):
        new_pixels[:, translate_x:] = old_pixels[:, :-translate_x]
    if translate_x < 0 or (wrap_x and translate_x != 0):
        new_pixels[:, :translate_x] = old_pixels[:, -translate_x:]
    # reset old pixels if translating on both axes
    if translate_x != 0 and translate_y != 0:
        old_pixels = new_pixels.copy()
    # translate y
    if translate_y > 0 or (wrap_y and translate_y != 0):
        new_pixels[translate_y:, :] = old_pixels[:-translate_y, :]
    if translate_y < 0 or (wrap_y and translate_y != 0):
        new_pixels[:translate_y, :] = old_pixels[-translate_y:, :]
    # reshape
    new_pixels = get_1d_pixel_array(new_pixels)
    return new_pixels
