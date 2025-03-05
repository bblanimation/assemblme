# Author: Christopher Gearhart

# System imports
from numba import jit, prange
import numpy as np

# Blender imports
# NONE!

# Module imports
# NONE!


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
