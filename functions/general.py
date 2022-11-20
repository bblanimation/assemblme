# Copyright (C) 2019 Christopher Gearhart
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
import random
import sys
import time
import os
import traceback
from os.path import join, dirname, abspath
from shutil import copyfile
from math import *

# Blender imports
import bpy
from bpy.props import *
props = bpy.props

# Module imports
from .common import *


def get_active_context_info(ag_idx=None):
    scn = bpy.context.scene
    ag_idx = ag_idx or scn.aglist_index
    ag = scn.aglist[ag_idx]
    return scn, ag


def assemblme_handle_exception():
    handle_exception(log_name="AssemblMe log", report_button_loc="AssemblMe > Animations > Report Error")


def get_randomized_orient(orient, random_amount):
    """ returns randomized orientation based on user settings """
    return orient + random.uniform(-random_amount, random_amount)


def get_offset_location(ag, loc):
    """ returns randomized location offset """
    loc_random = ag.loc_random
    loc_offset = ag.loc_offset
    sum_loc_offset = max(sum(loc_offset), 0.00001)
    X = loc.x + random.uniform(-loc_random, loc_random) * (loc_offset.x / sum_loc_offset) + loc_offset.x
    Y = loc.y + random.uniform(-loc_random, loc_random) * (loc_offset.y / sum_loc_offset) + loc_offset.y
    Z = loc.z + random.uniform(-loc_random, loc_random) * (loc_offset.z / sum_loc_offset) + loc_offset.z
    return (X, Y, Z)


def get_offset_rotation(ag, rot):
    """ returns randomized rotation offset """
    rot_random = ag.rot_random
    rot_offset = ag.rot_offset
    sum_rot_offset = max(sum(rot_offset), 0.00001)
    x = rot.x + random.uniform(-rot_random, rot_random) * (rot_offset.x / sum_rot_offset) + rot_offset.x
    y = rot.y + random.uniform(-rot_random, rot_random) * (rot_offset.y / sum_rot_offset) + rot_offset.y
    z = rot.z + random.uniform(-rot_random, rot_random) * (rot_offset.z / sum_rot_offset) + rot_offset.z
    return (x, y, z)


def get_build_speed(ag):
    """ calculates and returns build speed """
    return floor(ag.build_speed)


def get_object_velocity(ag):
    """ calculates and returns brick velocity """
    frameVelocity = round(2 ** (10 - ag.velocity))
    return frameVelocity


def get_anim_length(ag, objects_to_move, list_z_values, layer_height, inverted_build, skip_empty_selections):
    temp_obj_count = 0
    num_layers = 0
    last_lower_bound = None
    while len(objects_to_move) > temp_obj_count:
        objs, last_lower_bound = get_new_selection(list_z_values, layer_height, inverted_build, skip_empty_selections, last_lower_bound)
        num_objs = len(objs)
        num_layers += 1 if num_objs > 0 or not skip_empty_selections else 0
        temp_obj_count += num_objs
    return (num_layers - 1) * get_build_speed(ag) + get_object_velocity(ag) + 1


def get_preset_filenames(dir):
    """ list files in the given directory """
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and not f.startswith(".") and f.islower()]


def get_presets_filepath():
    return os.path.abspath(os.path.join(get_addon_directory(), "..", "..", "presets", "assemblme"))


def get_preset_tuples(self, context):
    # initialize presets path
    path = get_presets_filepath()
    # set up presets folder and transfer default presets
    if not os.path.exists(path):
        os.makedirs(path)
    if not bpy.app.background:
        transfer_defaults_to_preset_folder(path)
    # get list of filenames in presets directory
    filenames = get_preset_filenames(path)
    # refresh preset names
    filenames.sort()
    preset_names = [("None", "None", "Don't use a preset")]
    preset_names += [(filenames[i][:-3], filenames[i][:-3].replace("_", " ").capitalize(), "Select this preset!") for i in range(len(filenames))]
    return preset_names


def transfer_defaults_to_preset_folder(presets_path):
    default_presets_path = join(dirname(dirname(abspath(__file__))), "lib", "default_presets")
    filenames = get_preset_filenames(default_presets_path)
    if not os.path.exists(presets_path):
        os.mkdir(presets_path)
    for fn in filenames:
        dst = os.path.join(presets_path, fn)
        backup_dst = os.path.join(presets_path, "backups", fn)
        if os.path.isfile(dst):
            os.remove(dst)
        elif os.path.isfile(backup_dst):
            continue
        src = os.path.join(default_presets_path, fn)
        copyfile(src, dst)


def get_list_z_values(ag, objects, rot_x_l=False, rot_y_l=False):
    """ returns list of dicts containing objects and ther z locations relative to layer orientation """
    # assemble list of dictionaries into 'list_z_values'
    list_z_values = []
    if not rot_x_l:
        rot_x_l = [get_randomized_orient(ag.orient[0], ag.orient_random) for i in range(len(objects))]
        rot_y_l = [get_randomized_orient(ag.orient[1], ag.orient_random) for i in range(len(objects))]
    for i,obj in enumerate(objects):
        l = obj.matrix_world.to_translation() if ag.use_global else obj.location
        rot_x = rot_x_l[i]
        rot_y = rot_y_l[i]
        z_loc = (l.z * cos(rot_x) * cos(rot_y)) + (l.x * sin(rot_y)) + (l.y * -sin(rot_x))
        list_z_values.append({"loc":z_loc, "obj":obj})

    # sort list by "loc" key (relative z values)
    list_z_values.sort(key=lambda x: x["loc"], reverse=not ag.inverted_build)

    # return list of dictionaries
    return list_z_values, rot_x_l, rot_y_l


def get_objs_in_bound(list_z_values, z_lower_bound, inverted_build):
    """ select objects in bounds from list_z_values """
    objs_in_bound = []
    # iterate through objects in list_z_values (breaks when outside range)
    for i,lst in enumerate(list_z_values):
        # set obj and z_loc
        obj = lst["obj"]
        z_loc = lst["loc"]
        # check if object is in bounding z value
        if z_loc >= z_lower_bound and not inverted_build or z_loc <= z_lower_bound and inverted_build:
            objs_in_bound.append(obj)
        # if not, break for loop and pop previous objects from list_z_values
        else:
            for j in range(i):
                list_z_values.pop(0)
            break
    return objs_in_bound


def get_new_selection(list_z_values, layer_height, inverted_build, skip_empty_selections, last_lower_bound=None):
    """ selects next layer of objects """
    # get new upper and lower bounds
    z_upper_bound = list_z_values[0]["loc"] if skip_empty_selections or last_lower_bound is None else last_lower_bound
    z_lower_bound = z_upper_bound + layer_height * (1 if inverted_build else -1)
    # select objects in bounds
    objs_in_bound = get_objs_in_bound(list_z_values, z_lower_bound, inverted_build)
    return objs_in_bound, z_lower_bound


def set_bounds_for_visualizer(ag, list_z_values):
    for z_value in list_z_values:
        obj = z_value["obj"]
        if ag.mesh_only and obj.type != "MESH":
            continue
        ag.obj_min_loc = obj.location.copy()
        break
    for z_value in reversed(list_z_values):
        obj = z_value["obj"]
        if ag.mesh_only and obj.type != "MESH":
            continue
        ag.obj_max_loc = obj.location.copy()
        break


def layers(l):
    all = [False]*20
    if type(l) == int:
        all[l] = True
    elif type(l) == list:
        for l in lList:
            allL[l] = True
    elif l.lower() == "all":
        all = [True]*20
    elif l.lower() == "none":
        pass
    elif l.lower() == "active":
        all = list(bpy.context.scene.layers)
    else:
        sys.stderr.write("Argument passed to 'layers()' function not recognized")
    return all


def get_default_preset_names():
    default_preset_path = os.path.join(get_addon_directory(), "lib", "default_presets")
    return [os.path.splitext(fn)[0] for fn in os.listdir(default_preset_path) if fn.endswith(".py")]


def clear_animation(objs):
    objs = confirm_iter(objs)
    for obj in objs:
        obj.animation_data_clear()
    depsgraph_update()


def created_with_unsupported_version(ag):
    return ag.version[:3] != bpy.props.assemblme_version[:3]


def set_interpolation(objs, data_path, mode, start_frame=0, end_frame=1048574):
    objs = confirm_iter(objs)
    for obj in objs:
        if obj.animation_data is None:
            continue
        for fcurve in obj.animation_data.action.fcurves:
            if fcurve is None or not fcurve.data_path.startswith(data_path):
                continue
            for kf in fcurve.keyframe_points:
                if start_frame <= kf.co[0] <= end_frame:
                    kf.interpolation = mode


def animate_objects(ag, objects_to_move, list_z_values, cur_frame, loc_interpolation_mode='LINEAR', rot_interpolation_mode='LINEAR'):
    """ animates objects """

    # initialize variables for use in while loop
    objects_moved = []
    last_len_objects_moved = 0
    mult = 1 if ag.build_type == "ASSEMBLE" else -1
    inc  = 1 if ag.build_type == "ASSEMBLE" else 0
    velocity = get_object_velocity(ag)
    orig_frame = cur_frame
    insert_loc = any(ag.loc_offset) or ag.loc_random != 0
    insert_rot = any(ag.rot_offset) or ag.rot_random != 0
    layer_height = ag.layer_height
    inverted_build = ag.inverted_build
    skip_empty_selections = ag.skip_empty_selections
    kf_idx_loc = -1
    kf_idx_rot = -1
    last_lower_bound = None

    # insert first location keyframes
    if insert_loc:
        insert_keyframes(objects_to_move, "location", cur_frame + mult)
    # insert first rotation keyframes
    if insert_rot:
        insert_keyframes(objects_to_move, "rotation_euler", cur_frame + mult)

    while len(objects_to_move) > len(objects_moved):
        # print status to terminal
        update_progress_bars(True, True, len(objects_moved) / len(objects_to_move), last_len_objects_moved / len(objects_to_move), "Animating Layers")
        last_len_objects_moved = len(objects_moved)

        # get next objects to animate
        new_selection, last_lower_bound = get_new_selection(list_z_values, layer_height, inverted_build, skip_empty_selections, last_lower_bound)
        objects_moved += new_selection

        # move selected objects and add keyframes
        kf_idx_loc = -1
        kf_idx_rot = -1
        if len(new_selection) != 0:
            # insert location keyframes
            if insert_loc:
                loc_rand = random.uniform(-0.5, 0.5)
                insert_keyframes(new_selection, "location", cur_frame + loc_rand)
                kf_idx_loc -= inc
            # insert rotation keyframes
            if insert_rot:
                rot_rand = random.uniform(-0.5, 0.5)
                insert_keyframes(new_selection, "rotation_euler", cur_frame + rot_rand)
                kf_idx_rot -= inc

            # step cur_frame backwards
            cur_frame -= velocity * mult

            # move object and insert location keyframes
            if insert_loc:
                for obj in new_selection:
                    if ag.use_global:
                        obj.matrix_world.translation = get_offset_location(ag, obj.matrix_world.translation)
                    else:
                        obj.location = get_offset_location(ag, obj.location)
                insert_keyframes(new_selection, "location", cur_frame + loc_rand, if_needed=True)
            # rotate object and insert rotation keyframes
            if insert_rot:
                for obj in new_selection:
                    # if ag.use_global:
                    #     # TODO: Fix global rotation functionality
                    #     # NOTE: Solution 1 - currently limited to at most 360 degrees
                    #     xr, yr, zr = get_offset_rotation(ag, Vector((0,0,0)))
                    #     inv_mat = obj.matrix_world.inverted()
                    #     x_axis = mathutils_mult(inv_mat, Vector((1, 0, 0)))
                    #     y_axis = mathutils_mult(inv_mat, Vector((0, 1, 0)))
                    #     z_axis = mathutils_mult(inv_mat, Vector((0, 0, 1)))
                    #     x_mat = Matrix.Rotation(xr, 4, x_axis)
                    #     y_mat = Matrix.Rotation(yr, 4, y_axis)
                    #     z_mat = Matrix.Rotation(zr, 4, z_axis)
                    #     obj.matrix_local = mathutils_mult(z_mat, y_mat, x_mat, obj.matrix_local)
                    # else:
                    obj.rotation_euler = get_offset_rotation(ag, obj.rotation_euler)
                insert_keyframes(new_selection, "rotation_euler", cur_frame + rot_rand, if_needed=True)

            # step cur_frame forwards
            cur_frame += (velocity - get_build_speed(ag)) * mult

        # handle case where 'ag.skip_empty_selections' == False and empty selection is grabbed
        elif not ag.skip_empty_selections:
            # skip frame if nothing selected
            cur_frame -= get_build_speed(ag) * mult
        # handle case where 'ag.skip_empty_selections' == True and empty selection is grabbed
        else:
            os.stderr.write("Grabbed empty selection. This shouldn't happen!")

    cur_frame -= (velocity - get_build_speed(ag)) * mult
    # insert final location keyframes
    if insert_loc:
        insert_keyframes(objects_to_move, "location", cur_frame)
    # insert final rotation keyframes
    if insert_rot:
        insert_keyframes(objects_to_move, "rotation_euler", cur_frame)

    # set interpolation modes for moved objects
    start_frame = cur_frame if ag.build_type == "ASSEMBLE" else orig_frame
    end_frame = orig_frame if ag.build_type == "ASSEMBLE" else cur_frame
    set_interpolation(objects_moved, "loc", loc_interpolation_mode, start_frame, end_frame)
    set_interpolation(objects_moved, "rot", rot_interpolation_mode, start_frame, end_frame)

    update_progress_bars(True, True, 1, 0, "Animating Layers", end=True)

    return objects_moved, cur_frame


@blender_version_wrapper("<=", "2.79")
def get_anim_objects(ag, mesh_only:bool=None):
    if mesh_only is None: mesh_only = ag.mesh_only
    return [obj for obj in ag.collection.objects if obj.type == "MESH" or not mesh_only]
@blender_version_wrapper(">=", "2.80")
def get_anim_objects(ag, mesh_only:bool=None):
    if mesh_only is None: mesh_only = ag.mesh_only
    return [obj for obj in ag.collection.all_objects if obj.type == "MESH" or not mesh_only]


def match_properties(ag_new, ag_old):
    ag_new.build_speed = ag_old.build_speed
    ag_new.velocity = ag_old.velocity
    ag_new.layer_height = ag_old.layer_height
    ag_new.path_object = ag_old.path_object
    ag_new.loc_offset = ag_old.loc_offset
    ag_new.loc_random = ag_old.loc_random
    ag_new.rot_offset = ag_old.rot_offset
    ag_new.rot_random = ag_old.rot_random
    ag_new.loc_interpolation_mode = ag_old.loc_interpolation_mode
    ag_new.rot_interpolation_mode = ag_old.rot_interpolation_mode
    ag_new.orient = ag_old.orient
    ag_new.orient_random = ag_old.orient_random
    ag_new.build_type = ag_old.build_type
    ag_new.inverted_build = ag_old.inverted_build
    ag_new.use_global = ag_old.use_global
