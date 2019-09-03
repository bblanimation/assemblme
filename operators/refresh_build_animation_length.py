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
props = bpy.props

# Module imports
from ..functions import *

class ASSEMBLME_OT_refresh_anim_length(bpy.types.Operator):
    """Refreshes the box in UI with build animation length"""
    bl_idname = "assemblme.refresh_anim_length"
    bl_label = "Refresh Build Animation Length"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        ag = scn.aglist[scn.aglist_index]
        if ag.collection is None:
            return False
        return True

    def execute(self, context):
        try:
            # set up variables
            scn, ag = get_active_context_info()

            if ag.collection:
                # if objects in ag.collection, populate objects_to_move with them
                self.objects_to_move = get_anim_objects(ag)
                # set current_frame to animation start frame
                self.orig_frame = scn.frame_current
                bpy.context.scene.frame_set(ag.frame_with_orig_loc)
            else:
                # else, populate objects_to_move with selected_objects
                self.objects_to_move = context.selected_objects

            # populate self.list_z_values
            self.list_z_values,_,_ = get_list_z_values(ag, self.objects_to_move)

            # set props.obj_min_loc and props.obj_max_loc
            set_bounds_for_visualizer(ag, self.list_z_values)

            # calculate how many frames the animation will last (depletes self.list_z_values)
            ag.anim_length = get_anim_length(ag, self.objects_to_move, self.list_z_values, ag.layer_height, ag.inverted_build, ag.skip_empty_selections)

            if ag.collection:
                # set current_frame to original current_frame
                bpy.context.scene.frame_set(self.orig_frame)

            # reset upper and lower bound values
            props.z_upper_bound = None
            props.z_lower_bound = None
        except:
            assemblme_handle_exception()

        return{"FINISHED"}

    #############################################
