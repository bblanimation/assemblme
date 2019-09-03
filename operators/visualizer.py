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
import math

# Blender imports
import bpy
import bmesh
props = bpy.props

# Module imports
from ..functions import *

class ASSEMBLME_OT_visualizer(bpy.types.Operator):
    """Visualize the layer orientation with a plane"""
    bl_idname = "assemblme.visualize_layer_orientation"
    bl_label = "Visualize Layer Orientation"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    def modal(self, context, event):
        """ runs as long as visualizer is active """
        if event.type in {"ESC"}:
            self.full_disable(context)
            return{"CANCELLED"}

        if event.type == "TIMER":
            if context.scene.aglist_index == -1:
                self.full_disable(context)
                return{"CANCELLED"}
            scn, ag = get_active_context_info()
            try:
                v_obj = self.visualizer_obj
                # if the visualizer is has been disabled, stop running modal
                if not self.enabled():
                    self.full_disable(context)
                    return{"CANCELLED"}
                # if new build animation created, update visualizer animation
                if self.min_and_max != [props.obj_min_loc, props.obj_max_loc]:
                    self.min_and_max = [props.obj_min_loc, props.obj_max_loc]
                    self.create_vis_anim()
                # set visualizer object rotation
                if v_obj.rotation_euler.x != ag.orient[0]:
                    v_obj.rotation_euler.x = ag.orient[0]
                if v_obj.rotation_euler.y != ag.orient[1]:
                    v_obj.rotation_euler.y = ag.orient[1]
                if v_obj.rotation_euler.z != self.z_orient:
                    v_obj.rotation_euler.z = ag.orient[0] * (cos(ag.orient[1]) * sin(ag.orient[1]))
                    self.z_orient = v_obj.rotation_euler.z
                if scn.visualizer_scale != self.visualizer_scale or scn.visualizer_res != self.visualizer_res:
                    self.load_lattice_mesh(context)
                    v_obj.data.update()
            except:
                assemblme_handle_exception()

        return{"PASS_THROUGH"}

    def execute(self, context):
        try:
            scn, ag = get_active_context_info()
            # if enabled, all we do is disable it
            if self.enabled():
                self.full_disable(context)
                return{"FINISHED"}
            else:
                # ensure visualizer is hidden from render and selection
                self.visualizer_obj.hide_select = True
                self.visualizer_obj.hide_render = True
                # create animation for visualizer if build animation exists
                self.min_and_max = [props.obj_min_loc, props.obj_max_loc]
                if ag.collection is not None:
                    self.create_vis_anim()
                # enable visualizer
                self.enable(context)
                # initialize self.z_orient for modal
                self.z_orient = None
                # create timer for modal
                wm = context.window_manager
                self._timer = wm.event_timer_add(.02, window=context.window)
                wm.modal_handler_add(self)
        except:
            assemblme_handle_exception()

        return{"RUNNING_MODAL"}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        self.full_disable(context)

    ################################################
    # initialization method

    def __init__(self):
        self.visualizer_obj = bpy.data.objects.get("AssemblMe_visualizer")
        if self.visualizer_obj is None:
            # create visualizer object
            m = bpy.data.meshes.new("AssemblMe_visualizer_m")
            self.visualizer_obj = bpy.data.objects.new("AssemblMe_visualizer", m)

    #############################################
    # class methods

    def create_vis_anim(self):
        scn, ag = get_active_context_info()
        # if first and last location are the same, keep visualizer stationary
        if props.obj_min_loc == props.obj_max_loc or ag.orient_random > 0.0025:
            clear_animation(self.visualizer_obj)
            self.visualizer_obj.location = props.obj_min_loc if type(props.obj_min_loc) == type(self.visualizer_obj.location) else (0, 0, 0)
            ag.visualizer_animated = False
            return "static"
        # else, create animation
        else:
            # if animation already created, clear it
            if ag.visualizer_animated:
                clear_animation(self.visualizer_obj)
            # set up vars
            self.visualizer_obj.location = props.obj_min_loc
            cur_frame = ag.frame_with_orig_loc
            idx = -2 if ag.build_type == "ASSEMBLE" else -1
            mult = 1 if ag.build_type == "ASSEMBLE" else -1
            # insert keyframe and iterate current frame, and set another
            insert_keyframes(self.visualizer_obj, "location", cur_frame)
            self.visualizer_obj.location = props.obj_max_loc
            cur_frame -= (ag.anim_length - ag.last_layer_velocity) * mult
            insert_keyframes(self.visualizer_obj, "location", cur_frame, if_needed=True)
            ag.visualizer_animated = True
            set_interpolation(self.visualizer_obj, "loc", "LINEAR")

            return "animated"

    def load_lattice_mesh(self, context):
        scn = bpy.context.scene
        visualizer_bm = make_lattice(Vector((scn.visualizer_res, scn.visualizer_res, 1)), Vector([scn.visualizer_scale]*2 + [1]))
        self.visualizer_res = scn.visualizer_res
        self.visualizer_scale = scn.visualizer_scale
        visualizer_bm.to_mesh(self.visualizer_obj.data)

    def enable(self, context):
        """ enables visualizer """
        scn, ag = get_active_context_info()
        # alert user that visualizer is enabled
        self.report({"INFO"}, "Visualizer enabled... ('ESC' to disable)")
        # add proper mesh data to visualizer object
        self.load_lattice_mesh(context)
        # link visualizer object to scene
        safe_link(self.visualizer_obj)
        unhide(self.visualizer_obj)
        ag.visualizer_active = True

    def full_disable(self, context):
        """ disables visualizer """
        # alert user that visualizer is disabled
        self.report({"INFO"}, "Visualizer disabled")
        # unlink visualizer object
        safe_unlink(self.visualizer_obj)
        # disable visualizer icon
        for ag in bpy.context.scene.aglist:
            ag.visualizer_active = False

    @staticmethod
    def disable():
        """ static method for disabling visualizer """
        ag = get_active_context_info()[1]
        ag.visualizer_active = False

    @staticmethod
    def enabled():
        """ returns boolean for visualizer linked to scene """
        if bpy.context.scene.aglist_index == -1:
            return False
        ag = get_active_context_info()[1]
        return ag.visualizer_active

    #############################################
