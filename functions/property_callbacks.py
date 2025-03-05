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
    collections = bpy.data.collections
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
    clear_preset(self, context)
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


def clear_preset(self, context):
    # scn, ag = get_active_context_info()
    # ag.anim_preset = "None"
    pass


def handle_outdated_preset(self, context):
    scn, ag = get_active_context_info()
    clear_preset(self, context)
    if not ag.build_type.isupper():
        ag.build_type = str(ag.build_type).upper()


def update_anim_preset(self, context):
    scn, ag = get_active_context_info()
    if ag.anim_preset != "None":
        import importlib.util
        path_to_file = os.path.join(get_presets_filepath(), ag.anim_preset + ".py")
        if os.path.isfile(path_to_file):
            spec = importlib.util.spec_from_file_location(ag.anim_preset + ".py", path_to_file)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            foo.execute()
        else:
            bad_preset = str(ag.anim_preset)
            if bad_preset in get_default_preset_names():
                error_string = "Preset '%(bad_preset)s' could not be found. This is a default preset – try reinstalling the addon to restore it." % locals()
            else:
                error_string = "Preset '%(bad_preset)s' could not be found." % locals()
            sys.stderr.write(error_string)
            print(error_string)
            ag.anim_preset = "None"
    ag.cur_preset = ag.anim_preset

    return None


def ag_update(self, context):
    """ select and make source or LEGO model active if scn.aglist_index changes """
    scn = context.scene
    obj = context.view_layer.objects.active
    if scn.aglist_index != -1:
        ag = scn.aglist[scn.aglist_index]
        # ag.anim_preset = ag.cur_preset
        coll = ag.collection
        if coll is not None and len(coll.objects) > 0:
            select(list(coll.objects), active=coll.objects[0], only=True)
            scn.assemblme.last_active_object_name = obj.name
