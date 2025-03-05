# Author: Christopher Gearhart

# System imports
import numpy as np

# Blender imports
# NONE!

# Module imports
# NONE!


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
