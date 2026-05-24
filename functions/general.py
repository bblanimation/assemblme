# Copyright (C) 2025 Christopher Gearhart
# chris@bricksbroughttolife.com
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
import random
import sys
import time
import os
import traceback
import importlib
from os.path import join, dirname, abspath
from shutil import copyfile
from math import *

# Blender imports
import bpy
from bpy.types import Object, Context
from mathutils import Matrix, Vector
from bpy.props import *

# Module imports
from .common import *
from .common.blender import *

REMOVED_DEFAULT_PRESETS = {
    "build_order",
    "domino_build",
    "hero_part_reveal",
    "looping_build_unbuild",
    "magnetic_snap",
    "micro_bounce_settle",
    "reverse_teardown",
    "spiral_assembly",
    "wave_build",
}


def get_active_context_info(ag_idx:int=None):
    scn = bpy.context.scene
    ag_idx = ag_idx or scn.aglist_index
    ag = scn.aglist[ag_idx]
    return scn, ag


def assemblme_handle_exception():
    handle_exception(log_name="AssemblMe log", report_button_loc="AssemblMe > Animations > Report Error")


def get_randomized_orient(orient:float, random_amount:float):
    """ returns randomized orientation based on user settings """
    return orient + random.uniform(-random_amount, random_amount)


def get_offset_location(ag, loc:Vector):
    """ returns randomized location offset """
    loc_random = ag.loc_random
    loc_offset = Vector(ag.loc_offset)
    loc = Vector(loc)
    if loc_random == 0:
        return loc + loc_offset
    sum_loc_offset = sum(abs(v) for v in loc_offset)
    if sum_loc_offset < 0.00001:
        loc_rand = Vector((random.uniform(-loc_random, loc_random) for _ in range(3)))
    else:
        loc_rand = Vector((random.uniform(-loc_random, loc_random) * (v / sum_loc_offset) for v in loc_offset))
    return loc + loc_offset + loc_rand


def get_offset_rotation(ag, rot:Vector):
    """ returns randomized rotation offset """
    rot_random = ag.rot_random
    rot_offset = Vector(ag.rot_offset)
    rot = Vector(rot)
    if rot_random == 0:
        return rot + rot_offset
    sum_rot_offset = sum(abs(v) for v in rot_offset)
    if sum_rot_offset < 0.00001:
        rot_rand = Vector((random.uniform(-rot_random, rot_random) for _ in range(3)))
    else:
        rot_rand = Vector((random.uniform(-rot_random, rot_random) * (v / sum_rot_offset) for v in rot_offset))
    return rot + rot_offset + rot_rand


def get_rotation_offset_matrix(ag):
    """ returns a world-space rotation offset matrix from AssemblMe settings """
    x, y, z = get_offset_rotation(ag, Vector((0, 0, 0)))
    return mathutils_mult(Matrix.Rotation(z, 4, "Z"), Matrix.Rotation(y, 4, "Y"), Matrix.Rotation(x, 4, "X"))


def apply_global_rotation_offset(obj:Object, ag):
    """ rotates an object around its own origin, using global XYZ axes """
    loc = obj.matrix_world.to_translation()
    rot_mx = get_rotation_offset_matrix(ag)
    obj.matrix_world = mathutils_mult(Matrix.Translation(loc), rot_mx, Matrix.Translation(-loc), obj.matrix_world)


def set_object_world_location(obj:Object, loc:Vector):
    """ sets world location while preserving parent/local transform relationships """
    obj.matrix_world.translation = Vector(loc)


def get_build_speed(ag):
    """ calculates and returns build speed """
    return floor(ag.build_speed)


def get_object_velocity(ag):
    """ calculates and returns brick velocity """
    frameVelocity = round(2 ** (10 - ag.velocity))
    return frameVelocity


def get_anim_length(ag, objects_to_move:list[Object], list_z_values:list[dict[str, int|Object]], layer_height, inverted_build:bool, skip_empty_selections:bool):
    num_layers = len(get_layer_object_groups(list_z_values, layer_height, inverted_build, skip_empty_selections))
    return (num_layers - 1) * get_build_speed(ag) + get_object_velocity(ag) + 1


def get_anim_length_from_groups(ag, object_groups:list[list[Object]]):
    """ returns the animation length for precomputed object groups """
    return (max(1, len(object_groups)) - 1) * get_build_speed(ag) + get_object_velocity(ag) + 1


def get_layer_object_groups(list_z_values:list[dict[str, int|Object]], layer_height, inverted_build:bool, skip_empty_selections:bool):
    """ returns object groups using AssemblMe's classic layer-height selection """
    layer_groups = []
    working_z_values = list(list_z_values)
    object_count = len(working_z_values)
    selected_count = 0
    last_lower_bound = None
    while selected_count < object_count and len(working_z_values) > 0:
        objs, last_lower_bound = get_new_selection(working_z_values, layer_height, inverted_build, skip_empty_selections, last_lower_bound)
        if len(objs) > 0 or not skip_empty_selections:
            layer_groups.append(objs)
        selected_count += len(objs)
    return [group for group in layer_groups if len(group) > 0]


def get_build_order_groups(ag, objects_to_move:list[Object]):
    """ returns object groups from Bricker/LDraw build-order data when available """
    object_set = set(objects_to_move)
    groups = get_build_order_groups_from_bricker_model(ag, objects_to_move)
    if len(groups) == 0:
        groups = get_build_order_groups_from_steplists(ag, object_set)
    if len(groups) == 0:
        groups = get_build_order_groups_from_metadata(ag, objects_to_move)
    if len(groups) > 0:
        return apply_hero_final_split(groups, ag.build_order_hero_final_count)
    return []


def get_build_order_groups_from_bricker_model(ag, objects_to_move:list[Object]):
    """ reads cached Bricker bricksdict step/submodel metadata, when Bricker is available """
    bricker_functions = get_bricker_functions_module()
    if bricker_functions is None or not hasattr(bpy.context.scene, "cmlist"):
        return []
    cm = get_bricker_model_for_collection(ag)
    if cm is None:
        return []
    try:
        bricksdict = bricker_functions.get_bricksdict(cm)
    except Exception:
        return []
    if not bricksdict:
        return []
    objects_by_name = {obj.name: obj for obj in objects_to_move}
    groups_by_key = {}
    for index, brick_d in enumerate(bricksdict.values()):
        obj_name = brick_d.get("name")
        obj = objects_by_name.get(obj_name)
        if obj is None:
            continue
        step = brick_d.get("step_num")
        submodel = brick_d.get("submodel_name")
        if step is None and submodel is None:
            continue
        key = get_build_order_key(ag, step, submodel, index)
        groups_by_key.setdefault(key, []).append(obj)
    groups = [unique_objects(groups_by_key[key]) for key in sorted(groups_by_key)]
    return [group for group in groups if len(group) > 0]


def get_bricker_functions_module():
    """ imports Bricker functions only when Bricker is installed and loaded """
    module_name = getattr(bpy.props, "bricker_module_name", None)
    if module_name is None:
        return None
    try:
        return importlib.import_module(module_name + ".functions")
    except Exception:
        return None


def get_bricker_model_for_collection(ag):
    """ finds the Bricker model that owns the AssemblMe collection """
    target_collection = ag.collection
    if target_collection is None:
        return None
    for cm in bpy.context.scene.cmlist:
        cm_collection = getattr(cm, "collection", None)
        if cm_collection is None:
            continue
        if cm_collection == target_collection:
            return cm
        if hasattr(cm_collection, "children_recursive") and target_collection in cm_collection.children_recursive:
            return cm
    return None


def get_build_order_groups_from_steplists(ag, object_set:set[Object]):
    """ reads Bricker's collection steplist data without requiring a Bricker import """
    if ag.collection is None:
        return []
    groups = []
    collections = [ag.collection]
    if hasattr(ag.collection, "children_recursive"):
        collections += list(ag.collection.children_recursive)
    seen_objects = set()
    if ag.build_order_grouping == "SUBMODEL":
        child_collections = collections[1:] if len(collections) > 1 else collections
        return get_submodel_groups_from_collections(child_collections, object_set)
    for coll in collections:
        if not hasattr(coll, "steplist") or len(coll.steplist) == 0:
            continue
        for step_idx, step in enumerate(coll.steplist):
            step_objects = []
            for item in step.itemlist:
                step_objects += get_build_order_item_objects(item, object_set)
            step_objects = unique_objects(step_objects, seen_objects if ag.build_order_grouping != "SUBMODEL_STEP" else None)
            if len(step_objects) > 0:
                groups.append(step_objects)
    return groups


def get_submodel_groups_from_collections(collections:list, object_set:set[Object]):
    """ groups objects by child collection/submodel, useful for bag and submodel reveals """
    groups = []
    seen_objects = set()
    for coll in collections:
        if not hasattr(coll, "all_objects"):
            continue
        coll_objects = [obj for obj in coll.all_objects if obj in object_set]
        coll_objects = unique_objects(coll_objects, seen_objects)
        if len(coll_objects) > 0:
            groups.append(coll_objects)
    return groups


def get_build_order_item_objects(item, object_set:set[Object]):
    """ extracts objects from a Bricker step item """
    objs = []
    if getattr(item, "object", None) in object_set:
        objs.append(item.object)
    item_coll = getattr(item, "collection", None)
    if item_coll is not None and hasattr(item_coll, "all_objects"):
        objs += [obj for obj in item_coll.all_objects if obj in object_set]
    return objs


def get_build_order_groups_from_metadata(ag, objects_to_move:list[Object]):
    """ groups objects by step/submodel metadata stored on object custom properties """
    groups_by_key = {}
    for index, obj in enumerate(objects_to_move):
        key = get_object_build_order_key(ag, obj, index)
        if key is None:
            continue
        groups_by_key.setdefault(key, []).append(obj)
    return [groups_by_key[key] for key in sorted(groups_by_key)]


def get_object_build_order_key(ag, obj:Object, index:int):
    """ returns a sortable build-order key from object metadata """
    step = get_object_metadata_value(obj, ("assemblme_step", "bricker_step", "step_num", "step", "ldraw_step"))
    submodel = get_object_metadata_value(obj, ("assemblme_submodel", "bricker_submodel", "submodel_name", "submodel", "bag"))
    if step is None and submodel is None:
        return None
    return get_build_order_key(ag, step, submodel, index)


def get_build_order_key(ag, step, submodel, index:int=0):
    """ returns a sortable build-order key for a step/submodel pair """
    step = int(step) if isinstance(step, (int, float)) or str(step).lstrip("-").isdigit() else 0
    submodel = str(submodel) if submodel is not None else ""
    if ag.build_order_grouping == "SUBMODEL":
        return (natural_sort_key(submodel),)
    if ag.build_order_grouping == "SUBMODEL_STEP":
        return (natural_sort_key(submodel), step)
    return (step, natural_sort_key(submodel))


def get_object_metadata_value(obj:Object, keys:tuple[str]):
    """ fetches the first supported custom property from an object """
    for key in keys:
        if key in obj:
            return obj[key]
    return None


def natural_sort_key(value:str):
    """ gives stable human-ish sorting for submodel and bag names """
    parts = []
    cur = ""
    is_digit = False
    for ch in value:
        if ch.isdigit() != is_digit and cur:
            parts.append((0, int(cur)) if is_digit else (1, cur.lower()))
            cur = ""
        is_digit = ch.isdigit()
        cur += ch
    if cur:
        parts.append((0, int(cur)) if is_digit else (1, cur.lower()))
    return tuple(parts)


def unique_objects(objects:list[Object], seen_objects:set[Object]=None):
    """ removes duplicates while preserving order """
    unique = []
    local_seen = set()
    for obj in objects:
        if obj is None or obj in local_seen or (seen_objects is not None and obj in seen_objects):
            continue
        unique.append(obj)
        local_seen.add(obj)
        if seen_objects is not None:
            seen_objects.add(obj)
    return unique


def apply_hero_final_split(groups:list[list[Object]], hero_count:int):
    """ splits the final objects into one-by-one hero connection groups """
    if hero_count <= 0 or len(groups) == 0:
        return groups
    flat_tail = []
    remaining_groups = [list(group) for group in groups]
    while len(flat_tail) < hero_count and len(remaining_groups) > 0:
        if len(remaining_groups[-1]) == 0:
            remaining_groups.pop()
            continue
        flat_tail.insert(0, remaining_groups[-1].pop())
        if len(remaining_groups[-1]) == 0:
            remaining_groups.pop()
    return remaining_groups + [[obj] for obj in flat_tail]


def get_animation_object_groups(ag, objects_to_move:list[Object], list_z_values:list[dict[str, int|Object]]):
    """ returns final object groups for animation timing """
    if ag.order_mode == "BUILD_ORDER":
        groups = get_build_order_groups(ag, objects_to_move)
        if len(groups) > 0:
            return groups
        if not ag.build_order_fallback_layers:
            return []
    return get_layer_object_groups(list_z_values, ag.layer_height, ag.inverted_build, ag.skip_empty_selections)


def is_follow_curve_enabled(ag):
    """ returns whether a valid curve path should drive object location """
    path_obj = get_path_object(ag)
    if path_obj is not None and path_obj.type == "CURVE":
        return True
    preset = str(ag.anim_preset).lower().replace(" ", "_").replace("-", "_")
    return preset == "follow_curve"


def get_path_object(ag):
    """ returns the curve object selected for Follow Curve mode """
    if not ag.path_object:
        return None
    return bpy.data.objects.get(ag.path_object)


def get_bezier_point(p0, h0, h1, p1, t:float):
    """ samples a cubic bezier segment """
    return ((1 - t) ** 3 * p0) + (3 * (1 - t) ** 2 * t * h0) + (3 * (1 - t) * t ** 2 * h1) + (t ** 3 * p1)


def get_curve_path_points(path_obj:Object, samples_per_segment:int=12):
    """ returns world-space points from the longest spline on a curve object """
    if path_obj is None or path_obj.type != "CURVE":
        return []
    spline_paths = []
    for spline in path_obj.data.splines:
        points = []
        if spline.type == "BEZIER":
            bezier_points = list(spline.bezier_points)
            if len(bezier_points) < 2:
                continue
            segment_count = len(bezier_points) if spline.use_cyclic_u else len(bezier_points) - 1
            for i in range(segment_count):
                p0 = bezier_points[i]
                p1 = bezier_points[(i + 1) % len(bezier_points)]
                if i == 0:
                    points.append(mathutils_mult(path_obj.matrix_world, p0.co))
                for j in range(1, samples_per_segment + 1):
                    t = j / samples_per_segment
                    points.append(mathutils_mult(path_obj.matrix_world, get_bezier_point(p0.co, p0.handle_right, p1.handle_left, p1.co, t)))
        else:
            raw_points = spline.points
            if len(raw_points) < 2:
                continue
            points = [mathutils_mult(path_obj.matrix_world, Vector((p.co.x, p.co.y, p.co.z))) for p in raw_points]
            if spline.use_cyclic_u:
                points.append(points[0].copy())
        if spline.use_cyclic_u and len(points) > 2 and (points[-1] - points[0]).length < 0.00001:
            points.pop()
        if len(points) > 1:
            spline_paths.append(points)
    if len(spline_paths) == 0:
        return []
    return max(spline_paths, key=get_polyline_length)


def get_polyline_length(points:list[Vector]):
    """ returns total length of a polyline """
    return sum((points[i] - points[i - 1]).length for i in range(1, len(points)))


def get_point_on_polyline(points:list[Vector], factor:float):
    """ samples a point from a polyline by normalized distance """
    factor = min(1, max(0, factor))
    if len(points) == 0:
        return None
    if len(points) == 1:
        return points[0].copy()
    total_length = get_polyline_length(points)
    if total_length <= 0:
        return points[0].copy()
    target_length = total_length * factor
    walked = 0
    for i in range(1, len(points)):
        segment = points[i] - points[i - 1]
        segment_length = segment.length
        if walked + segment_length >= target_length:
            segment_factor = (target_length - walked) / segment_length if segment_length > 0 else 0
            return points[i - 1].lerp(points[i], segment_factor)
        walked += segment_length
    return points[-1].copy()


def get_curve_relative_location(points:list[Vector], final_loc:Vector, factor:float):
    """ maps a curve sample to an object's final location, using the curve end as the anchor """
    path_loc = get_point_on_polyline(points, factor)
    if path_loc is None:
        return final_loc
    return Vector(final_loc) + (path_loc - points[-1])


def keyframe_object_on_curve(obj:Object, points:list[Vector], final_loc:Vector, factor:float, frame:float):
    """ places an object on the relative curve path and keyframes its local location """
    set_object_world_location(obj, get_curve_relative_location(points, final_loc, factor))
    obj.keyframe_insert(data_path="location", frame=frame)


def insert_follow_curve_keyframes(obj:Object, points:list[Vector], final_loc:Vector, final_frame:float, path_frame:float, frame_random:float=0):
    """ inserts enough location keys for an object to visibly follow a curve """
    start_frame = min(final_frame, path_frame)
    end_frame = max(final_frame, path_frame)
    duration = max(1, end_frame - start_frame)
    steps = min(12, max(3, int(duration / 4)))
    assembling = path_frame < final_frame
    for i in range(1, steps):
        progress = i / steps
        factor = progress if assembling else 1 - progress
        frame = start_frame + duration * progress + frame_random
        keyframe_object_on_curve(obj, points, final_loc, factor, frame)
    keyframe_object_on_curve(obj, points, final_loc, 0, path_frame + frame_random)


def get_preset_filenames(dir:str):
    """ list files in the given directory """
    return [
        f for f in os.listdir(dir)
        if os.path.isfile(os.path.join(dir, f)) and
        not f.startswith(".") and
        f.islower() and
        os.path.splitext(f)[0] not in REMOVED_DEFAULT_PRESETS
    ]


def get_presets_filepath():
    return os.path.abspath(os.path.join(get_addon_directory(), "..", "..", "presets", "assemblme"))


def get_preset_tuples(self, context:Context):
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


def transfer_defaults_to_preset_folder(presets_path:str):
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


def get_list_z_values(ag, objects:list[Object], rot_x_l:bool=False, rot_y_l:bool=False):
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


def get_objs_in_bound(list_z_values:list[dict[str, int|Object]], z_lower_bound:int, inverted_build:bool):
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


def get_new_selection(list_z_values:list[dict[str, int|Object]], layer_height:int, inverted_build:bool, skip_empty_selections:bool, last_lower_bound:int=None):
    """ selects next layer of objects """
    # get new upper and lower bounds
    z_upper_bound = list_z_values[0]["loc"] if skip_empty_selections or last_lower_bound is None else last_lower_bound
    z_lower_bound = z_upper_bound + layer_height * (1 if inverted_build else -1)
    # select objects in bounds
    objs_in_bound = get_objs_in_bound(list_z_values, z_lower_bound, inverted_build)
    return objs_in_bound, z_lower_bound


def set_bounds_for_visualizer(ag, list_z_values:list[dict[str, int|Object]]):
    for z_value in list_z_values:
        obj = z_value["obj"]
        if ag.mesh_only and obj.type != "MESH":
            continue
        ag.obj_min_loc = obj.matrix_world.to_translation() if ag.use_global else obj.location.copy()
        break
    for z_value in reversed(list_z_values):
        obj = z_value["obj"]
        if ag.mesh_only and obj.type != "MESH":
            continue
        ag.obj_max_loc = obj.matrix_world.to_translation() if ag.use_global else obj.location.copy()
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


def clear_animation(objs:list[Object]):
    objs = confirm_iter(objs)
    for obj in objs:
        obj.animation_data_clear()
    depsgraph_update()


def created_with_unsupported_version(ag):
    return ag.version[:3] != bpy.props.assemblme_version[:3]


@blender_version_wrapper(">=", "5.0")
def set_interpolation(objs, data_path, mode, start_frame=0, end_frame=1048574):
    objs = confirm_iter(objs)
    for obj in objs:
        if obj.animation_data is None:
            continue
        action = obj.animation_data.action
        for fcurve in action.layers[0].strips[0].channelbag(action.slots[0]).fcurves:
            if fcurve is None or not fcurve.data_path.startswith(data_path):
                continue
            for kf in fcurve.keyframe_points:
                if start_frame <= kf.co[0] <= end_frame:
                    kf.interpolation = mode
@blender_version_wrapper("<", "5.0")
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


def animate_objects(ag, objects_to_move:list[Object], list_z_values:list[dict[str, int|Object]], cur_frame:int, loc_interpolation_mode:str="LINEAR", rot_interpolation_mode:str="LINEAR", object_groups:list[list[Object]]=None):
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
    follow_curve = is_follow_curve_enabled(ag)
    path_points = get_curve_path_points(get_path_object(ag)) if follow_curve else []
    object_groups = object_groups if object_groups is not None else get_animation_object_groups(ag, objects_to_move, list_z_values)
    kf_idx_loc = -1
    kf_idx_rot = -1

    # insert first location keyframes
    if insert_loc or follow_curve:
        insert_keyframes(objects_to_move, "location", cur_frame + mult)
    # insert first rotation keyframes
    if insert_rot and not follow_curve:
        insert_keyframes(objects_to_move, "rotation_euler", cur_frame + mult)

    for new_selection in object_groups:
        # print status to terminal
        update_progress_bars(True, True, len(objects_moved) / len(objects_to_move), last_len_objects_moved / len(objects_to_move), "Animating Layers")
        last_len_objects_moved = len(objects_moved)
        objects_moved += new_selection

        # move selected objects and add keyframes
        kf_idx_loc = -1
        kf_idx_rot = -1
        if len(new_selection) != 0:
            final_frame = cur_frame
            final_locs = {obj: obj.matrix_world.to_translation().copy() for obj in new_selection}
            # insert location keyframes
            if insert_loc or follow_curve:
                loc_rand = random.uniform(-0.5, 0.5)
                insert_keyframes(new_selection, "location", cur_frame + loc_rand)
                kf_idx_loc -= inc
            # insert rotation keyframes
            if insert_rot and not follow_curve:
                rot_rand = random.uniform(-0.5, 0.5)
                insert_keyframes(new_selection, "rotation_euler", cur_frame + rot_rand)
                kf_idx_rot -= inc

            # step cur_frame backwards
            cur_frame -= velocity * mult

            # move object and insert location keyframes
            if follow_curve and len(path_points) > 1:
                for obj in new_selection:
                    insert_follow_curve_keyframes(obj, path_points, final_locs[obj], final_frame, cur_frame, loc_rand)
            elif insert_loc:
                for obj in new_selection:
                    if ag.use_global:
                        set_object_world_location(obj, get_offset_location(ag, obj.matrix_world.translation))
                    else:
                        obj.location = get_offset_location(ag, obj.location)
                insert_keyframes(new_selection, "location", cur_frame + loc_rand, if_needed=True)
            # rotate object and insert rotation keyframes
            if insert_rot and not follow_curve:
                for obj in new_selection:
                    if ag.use_global:
                        apply_global_rotation_offset(obj, ag)
                    else:
                        obj.rotation_euler = get_offset_rotation(ag, obj.rotation_euler)
                insert_keyframes(new_selection, "rotation_euler", cur_frame + rot_rand, if_needed=True)

            # step cur_frame forwards
            cur_frame += (velocity - get_build_speed(ag)) * mult

    cur_frame -= (velocity - get_build_speed(ag)) * mult
    # insert final location keyframes
    if insert_loc or follow_curve:
        insert_keyframes(objects_to_move, "location", cur_frame)
    # insert final rotation keyframes
    if insert_rot and not follow_curve:
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
    ag_new.order_mode = ag_old.order_mode
    ag_new.build_order_grouping = ag_old.build_order_grouping
    ag_new.build_order_hero_final_count = ag_old.build_order_hero_final_count
    ag_new.build_order_fallback_layers = ag_old.build_order_fallback_layers
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
