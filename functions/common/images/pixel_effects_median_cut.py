# Author: Christopher Gearhart

# System imports
import numpy as np
import time

# Blender imports
# NONE!

# Module imports
from .pixel_effects_reshape import *


#######################################################
#########     MEDIAN CUT CLUSTERING      ##############
#######################################################


def cluster_pixels(pix_1d, depth, channels):
    pix_2d = get_2d_pixel_array(pix_1d, channels)
    new_pix_2d = np.empty(pix_2d.shape, dtype=np.float32)

    new_shape = (len(pix_2d), channels + 1)
    pix_2d_with_idxs = np.empty(new_shape, dtype=np.float64)
    pix_2d_with_idxs[:, :-1] = pix_2d
    pix_2d_with_idxs[:, -1:] = np.arange(len(pix_2d), dtype=np.int64).reshape((len(pix_2d), 1))

    split_into_buckets(new_pix_2d, pix_2d_with_idxs, depth, channels)

    new_pix_1d = new_pix_2d.reshape(len(pix_1d))
    return new_pix_1d


# Adapted and improved from: https://muthu.co/reducing-the-number-of-colors-of-an-image-using-median-cut-algorithm/
def median_cut_quantize(new_img_arr, img_arr, channels):
    # when it reaches the end, color quantize
    # print("to quantize: ", len(img_arr))
    color_ave = [np.mean(img_arr[:,i]) for i in range(channels)]

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

    # ct = time.time()
    ranges = []
    for i in range(channels):
        channel_vals = img_arr[:,i]
        ranges.append(np.max(channel_vals) - np.min(channel_vals))
    # ct = stopwatch("1---", ct)

    space_with_highest_range = ranges.index(max(ranges))
    # print("space_with_highest_range:", space_with_highest_range)
    # sort the image pixels by color space with highest range
    # ct = time.time()
    img_arr = img_arr[img_arr[:,space_with_highest_range].argsort()]
    # ct = stopwatch("2-------", ct)
    # find the median to divide the array.
    median_index = (len(img_arr) + 1) // 2
    # print("median_index:", median_index)

    #split the array into two buckets along the median
    split_into_buckets(new_img_arr, img_arr[:median_index], depth - 1, channels)
    split_into_buckets(new_img_arr, img_arr[median_index:], depth - 1, channels)
