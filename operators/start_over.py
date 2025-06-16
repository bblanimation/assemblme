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
import time

# Blender imports
import bpy
props = bpy.props

# Module imports
from ..functions import *

class ASSEMBLME_OT_start_over(bpy.types.Operator):
    """Clear animation from objects moved in last 'Create Build Animation' action"""
    bl_idname = "assemblme.start_over"
    bl_label = "Start Over"
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
        if ag.animated:
            return True
        return False

    def execute(self, context):
        try:
            self.start_over()
        except:
            assemblme_handle_exception()
        return{"FINISHED"}

    ###################################################
    # initialization method

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orig_frame = bpy.context.scene.frame_current

    ###################################################
    # class methods

    @timed_call("Time Elapsed")
    def start_over(self):
        # initialize vars
        scn, ag = get_active_context_info()
        ag.visualizer_needs_update = True

        # set current_frame to animation start frame
        all_ags_for_collection = [ag0 for ag0 in scn.aglist if ag0 == ag or (ag0.collection == ag.collection and ag0.animated)]
        all_ags_for_collection.sort(key=lambda x: x.time_created)
        # set frame to frame_with_orig_loc that was created first (all_ags_for_collection are sorted by time created)
        scn.frame_set(all_ags_for_collection[0].frame_with_orig_loc)

        # clear obj_min_loc and obj_max_loc
        ag.obj_min_loc, ag.obj_max_loc = (0, 0, 0), (0, 0, 0)

        # clear animation data from all objects in 'AssemblMe_all_objects_moved' group/collection
        if ag.collection is not None:
            print("\nClearing animation data from " + str(len(get_anim_objects(ag))) + " objects.")
            clear_animation(get_anim_objects(ag))

        # set current_frame to original current_frame
        scn.frame_set(self.orig_frame)

        # set all animated groups as not animated
        for ag0 in all_ags_for_collection:
            ag0.animated = False
            ag0.time_created = float("inf")

    #############################################
