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
# NONE!

# Blender imports
import bpy

# Addon imports
from ..functions import *



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
