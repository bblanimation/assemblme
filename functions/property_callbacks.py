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
from operator import itemgetter

# Blender imports
import bpy
from bpy.props import *

# Module imports
from .general import *


def uniquify_name(self, context):
    """ if LEGO model exists with name, add '.###' to the end """
    scn, ag = get_active_context_info()
    name = ag.name
    while scn.aglist.keys().count(name) > 1:
        if name[-4] == ".":
            try:
                num = int(name[-3:])+1
            except:
                num = 1
            name = name[:-3] + "%03d" % (num)
        else:
            name = name + ".001"
    if ag.name != name:
        ag.name = name


def collection_update(self, context):
    scn, ag0 = get_active_context_info()
    # get rid of unused groups created by AssemblMe
    collections = bpy.data.collections if b280() else bpy.data.groups
    for c in collections:
        if c.name.startswith("AssemblMe_"):
            success = False
            for i in range(len(scn.aglist)):
                ag0 = scn.aglist[i]
                if c.name == "AssemblMe_{}_collection".format(ag0.name):
                    success = True
            if not success:
                collections.remove(c, do_unlink=True)


def set_meshes_only(self, context):
    scn, ag = get_active_context_info()
    objs_to_clear = []
    if ag.collection is not None and ag.mesh_only:
        objs_to_clear = [obj for obj in get_anim_objects(ag, mesh_only=False) if obj.type != "MESH"]
    if ag.animated and len(objs_to_clear) > 0:
        # set current_frame to animation start frame
        orig_frame = scn.frame_current
        scn.frame_set(ag.frame_with_orig_loc)
        # clear animation
        clear_animation(objs_to_clear)
        # set current_frame back to to original frame
        scn.frame_set(orig_frame)


def handle_outdated_preset(self, context):
    scn, ag = get_active_context_info()
    if not ag.build_type.isupper():
        ag.build_type = str(ag.build_type).upper()


def update_anim_preset(self, context):
    scn = bpy.context.scene
    if scn.anim_preset != "None":
        import importlib.util
        path_to_file = os.path.join(get_presets_filepath(), scn.anim_preset + ".py")
        if os.path.isfile(path_to_file):
            spec = importlib.util.spec_from_file_location(scn.anim_preset + ".py", path_to_file)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            foo.execute()
        else:
            bad_preset = str(scn.anim_preset)
            if bad_preset in get_default_preset_names():
                error_string = "Preset '%(bad_preset)s' could not be found. This is a default preset – try reinstalling the addon to restore it." % locals()
            else:
                error_string = "Preset '%(bad_preset)s' could not be found." % locals()
            sys.stderr.write(error_string)
            print(error_string)
            preset_names = get_preset_tuples()

            bpy.types.Scene.anim_preset = EnumProperty(
                name="Presets",
                description="Stored AssemblMe presets",
                items=preset_names,
                update=update_anim_preset,
                default="None",
            )

            bpy.types.Scene.anim_preset_to_delete = EnumProperty(
                name="Preset to Delete",
                description="Another list of stored AssemblMe presets",
                items=preset_names,
                default="None",
            )
            scn.anim_preset = "None"
    scn, ag = get_active_context_info()
    ag.cur_preset = scn.anim_preset

    return None
