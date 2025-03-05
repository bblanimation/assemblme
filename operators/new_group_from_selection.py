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
import bpy

# Blender imports
import time

# Module imports
from ..functions import *

class ASSEMBLME_OT_new_group_from_selection(bpy.types.Operator):
    """Create new group/collection for animation containing selected objects"""
    bl_idname = "assemblme.new_group_from_selection"
    bl_label = "New Collection"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        return True

    def execute(self, context):
        if not self.can_run():
            return{"CANCELLED"}
        try:
            scn, ag = get_active_context_info()
            # create new animated collection
            new_coll_name = "AssemblMe_{}_collection".format(ag.name)
            overwrite_coll = bpy.data.collections.get(new_coll_name)
            if overwrite_coll is not None:
                bpy.data.collections.remove(overwrite_coll)
            ag.collection = bpy.data.collections.new(new_coll_name)
            # add selected objects to new group
            for obj in self.objs_to_move:
                ag.collection.objects.link(obj)
        except:
            assemblme_handle_exception()

        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        scn, ag = get_active_context_info()
        self.objs_to_move = [obj for obj in bpy.context.selected_objects if not ag.mesh_only or obj.type == "MESH"]

    ################################################
    # class method

    def can_run(self):
        if len(self.objs_to_move) == 0:
            self.report({"WARNING"}, "No objects selected")
            return False
        return True

    #############################################
