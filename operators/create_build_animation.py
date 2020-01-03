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
from bpy.props import *

# Module imports
from ..functions import *

class ASSEMBLME_OT_create_build_animation(bpy.types.Operator):
    """Select objects layer by layer and shift by given values"""
    bl_idname = "assemblme.create_build_animation"
    bl_label = "Create Build Animation"
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
        try:
            scn, ag = get_active_context_info()
            all_ags_for_collection = [ag0 for ag0 in scn.aglist if ag0 == ag or (ag0.collection == ag.collection and ag0.animated)]
            all_ags_for_collection.sort(key=lambda x: x.time_created)
            # ensure operation can run
            if not self.is_valid(scn, ag):
                return {"CANCELLED"}
            # set frame to frame_with_orig_loc that was created first (all_ags_for_collection are sorted by time created)
            scn.frame_set(all_ags_for_collection[0].frame_with_orig_loc)
            # clear animation data from all objects in ag.collection
            clear_animation(get_anim_objects(ag))
            # create current animation (and recreate any others for this collection that were cleared)
            for ag0 in all_ags_for_collection:
                self.create_anim(scn, ag0)
            # set current_frame to original current_frame
            scn.frame_set(self.orig_frame)
            ag.visualizer_needs_update = True
        except:
            assemblme_handle_exception()
            return{"CANCELLED"}
        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        scn, ag = get_active_context_info()
        if ag.collection is not None:
            self.objects_to_move = [obj for obj in get_anim_objects(ag) if not ag.mesh_only or obj.type == "MESH"]
        self.orig_frame = scn.frame_current

    ###################################################
    # class variables

    # NONE!

    ###################################################
    # class methods

    @timed_call("Time Elapsed")
    def create_anim(self, scn, ag):
        print("\ncreating build animation...")

        # initialize vars
        action = "UPDATE" if ag.animated else "CREATE"
        ag.last_layer_velocity = get_object_velocity(ag)
        if action == "CREATE":
            ag.time_created = time.time()

        # set current_frame to a frame where the animation is in it's initial state (if creating, this was done in 'execute')
        scn.frame_set(ag.frame_with_orig_loc if action == "UPDATE" else ag.first_frame)

        ### BEGIN ANIMATION GENERATION ###
        # populate self.list_z_values
        self.list_z_values,rot_x_l,rot_y_l = get_list_z_values(ag, self.objects_to_move)

        # set obj_min_loc and obj_max_loc
        set_bounds_for_visualizer(ag, self.list_z_values)

        # calculate how many frames the animation will last
        ag.anim_length = get_anim_length(ag, self.objects_to_move, self.list_z_values.copy(), ag.layer_height, ag.inverted_build, ag.skip_empty_selections)

        # set first frame to animate from
        self.cur_frame = ag.first_frame + (ag.anim_length if ag.build_type == "ASSEMBLE" else 0)

        # set frame_with_orig_loc for 'Start Over' operation
        ag.frame_with_orig_loc = self.cur_frame

        # animate the objects
        objects_moved, last_frame = animate_objects(ag, self.objects_to_move, self.list_z_values, self.cur_frame, ag.loc_interpolation_mode, ag.rot_interpolation_mode)

        # handle case where no object was ever selected (e.g. only camera passed to function).
        if action == "CREATE" and ag.frame_with_orig_loc == last_frame:
            warning_msg = "No valid objects selected!"
            if ag.mesh_only:
                warning_msg += " (Non-mesh objects ignored – see advanced settings)"
            self.report({"WARNING"}, warning_msg)
            return{"FINISHED"}

        # define animation start and end frames
        ag.anim_bounds_start = ag.first_frame if ag.build_type == "ASSEMBLE" else ag.first_frame
        ag.anim_bounds_end   = ag.frame_with_orig_loc if ag.build_type == "ASSEMBLE" else last_frame

        # disable relationship lines and mark as animated
        if action == "CREATE":
            disable_relationship_lines()
            ag.animated = True

    def is_valid(self, scn, ag):
        if ag.collection is None:
            self.report({"WARNING"}, "No collection name specified" if b280() else "No group name specified")
            return False
        if len(get_anim_objects(ag)) == 0:
            self.report({"WARNING"}, "Collection contains no objects!" if b280() else "Group contains no objects!")
            return False
        # check if this would overlap with other animations
        other_anim_ags = [ag0 for ag0 in scn.aglist if ag0 != ag and ag0.collection == ag.collection and ag0.animated]
        for ag1 in other_anim_ags:
            if ag1.anim_bounds_start <= ag.first_frame and ag.first_frame <= ag1.anim_bounds_end:
                self.report({"WARNING"}, "Animation overlaps with another AssemblMe aninmation for this collection")
                return False
        # make sure no objects in this collection are part of another AssemblMe animation
        for i in range(len(scn.aglist)):
            c = scn.aglist[i].collection
            if i == scn.aglist_index or not scn.aglist[i].animated or c.name == ag.collection.name:
                continue
            for obj in self.objects_to_move:
                users_collection = obj.users_collection if b280() else obj.users_group
                if c in users_collection:
                    self.report({"ERROR"}, "Some objects in this collection are part of another AssemblMe animation")
                    return False
        return True

    #############################################
