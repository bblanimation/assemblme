# Author: Christopher Gearhart

# System imports
from numba import cuda, jit, prange
import numpy as np
from colorsys import rgb_to_hsv, hsv_to_rgb

# Blender imports
# NONE!

# Module imports
# from .color_effects_cuda import *
from .images import *


def initialize_gradient_texture(width, height, quadratic=False):
    pixels = np.empty((height, width))
    for row in prange(height):
        val = 1 - (height - 1 - row) / (height - 1)
        if quadratic:
            val = val ** 0.5
        pixels[row, :] = val
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


@jit(nopython=True, parallel=True)
def resize_pixels(size, channels, old_pixels, old_size):
    new_pixels = np.empty(size[0] * size[1] * channels)
    for col in prange(size[0]):
        col1 = int((col / size[0]) * old_size[0])
        for row in range(size[1]):
            row1 = int((row / size[1]) * old_size[1])
            pixel_number = (size[0] * row + col) * channels
            pixel_number_ref = (old_size[0] * row1 + col1) * channels
            for ch in range(channels):
                new_pixels[pixel_number + ch] = old_pixels[pixel_number_ref + ch]
    return new_pixels


@jit(nopython=True, parallel=True)
def resize_pixels_preserve_borders(size, channels, old_pixels, old_size):
    new_pixels = np.empty(len(old_pixels))
    offset_col = int((old_size[0] - size[0]) / 2)
    offset_row = int((old_size[1] - size[1]) / 2)
    for col in prange(old_size[0]):
        col1 = int(((col - offset_col) / size[0]) * old_size[0])
        for row in range(old_size[1]):
            row1 = int(((row - offset_row) / size[1]) * old_size[1])
            pixel_number = (old_size[0] * row + col) * channels
            if 0 <= col1 < old_size[0] and 0 <= row1 < old_size[1]:
                pixel_number_ref = (old_size[0] * row1 + col1) * channels
                for ch in range(channels):
                    new_pixels[pixel_number + ch] = old_pixels[pixel_number_ref + ch]
            else:
                for ch in range(channels):
                    new_pixels[pixel_number + ch] = 0
    return new_pixels


def crop_pixels(size, channels, old_pixels, old_size):
    old_pixels = get_3d_pixel_array(old_pixels, old_size[0], old_size[1], channels)
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


def blend_pixels(im1_pixels, im2_pixels, width, height, channels, operation, use_clamp, factor_pixels):
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
    #     for i in prange(new_pixels.size):
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


@jit(nopython=True, parallel=True)
def dilate_pixels_dist(old_pixels, pixel_dist, width, height):
    mult = 1 if pixel_dist[0] > 0 else -1
    new_pixels = np.empty(len(old_pixels))
    # for i in prange(width * height):
    #     x = i / height
    #     row = round((x % 1) * height)
    #     col = round(x - (x % 1))
    for col in prange(width):
        for row in prange(height):
            pixel_number = width * row + col
            max_val = old_pixels[pixel_number]
            for c in range(-pixel_dist[0], pixel_dist[0] + 1):
                for r in range(-pixel_dist[1], pixel_dist[1] + 1):
                    if not (0 < col + c < width and 0 < row + r < height):
                        continue
                    width_amt = abs(c) / pixel_dist[0]
                    height_amt = abs(r) / pixel_dist[1]
                    ratio = (width_amt - height_amt) / 2 + 0.5
                    weighted_dist = pixel_dist[0] * ratio + ((1 - ratio) * pixel_dist[1])
                    dist = ((abs(c)**2 + abs(r)**2) ** 0.5)
                    if dist > weighted_dist + 0.5:
                        continue
                    pixel_number1 = width * (row + r) + (col + c)
                    cur_val = old_pixels[pixel_number1]
                    if cur_val * mult > max_val * mult:
                        max_val = cur_val
            new_pixels[pixel_number] = max_val
    return new_pixels


@jit(nopython=True, parallel=True)
def dilate_pixels_step(old_pixels, pixel_dist, width, height):
    mult = 1 if pixel_dist[0] > 0 else -1
    new_pixels = np.empty(len(old_pixels))
    # for i in prange(width * height):
    #     x = i / height
    #     row = round((x % 1) * height)
    #     col = round(x - (x % 1))
    for col in prange(width):
        for row in range(height):
            pixel_number = width * row + col
            max_val = old_pixels[pixel_number]
            for c in range(-pixel_dist[0], pixel_dist[0] + 1):
                if not 0 < col + c < width:
                    continue
                pixel_number1 = width * row + (col + c)
                cur_val = old_pixels[pixel_number1]
                if cur_val * mult > max_val * mult:
                    max_val = cur_val
            new_pixels[pixel_number] = max_val
    old_pixels = new_pixels
    new_pixels = np.empty(len(old_pixels))
    for col in prange(width):
        for row in range(height):
            pixel_number = width * row + col
            max_val = old_pixels[pixel_number]
            for r in range(-pixel_dist[1], pixel_dist[1] + 1):
                if not 0 < row + r < height:
                    continue
                pixel_number1 = width * (row + r) + col
                cur_val = old_pixels[pixel_number1]
                if cur_val * mult > max_val * mult:
                    max_val = cur_val
            new_pixels[pixel_number] = max_val
    return new_pixels


def flip_pixels(old_pixels, flip_x, flip_y, width, height, channels):
    old_pixels = get_3d_pixel_array(old_pixels, width, height, channels)
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
