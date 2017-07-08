"""
    Copyright (C) 2017 Bricks Brought to Life
    http://bblanimation.com/
    chris@bblanimation.com

    Created by Christopher Gearhart

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <http://www.gnu.org/licenses/>.
    """

# system imports
import bpy
import math
from ..functions import *
props = bpy.props

class visualizer(bpy.types.Operator):
    """Visualize the layer orientation with a plane"""                          # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.visualize_layer_orientation"                             # unique identifier for buttons and menu items to reference.
    bl_label = "Visualize Layer Orientation"                                    # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    def createAnim(self):
        scn = bpy.context.scene

        if props.objMinLoc == props.objMaxLoc:
            self.visualizerObj.animation_data_clear()
            if type(props.objMinLoc) == type(self.visualizerObj.location):
                self.visualizerObj.location = props.objMinLoc
            else:
                self.visualizerObj.location = (0,0,0)
            return

        self.visualizerObj.location = props.objMinLoc
        curFrame = scn.frameWithOrigLoc

        insertKeyframes(self.visualizerObj, "location", curFrame)
        self.visualizerObj.location = props.objMaxLoc
        if scn.buildType == "Assemble":
            curFrame -= (scn.animLength - scn.lastLayerVelocity)
        else:
            curFrame += (scn.animLength - scn.lastLayerVelocity)
        insertKeyframes(self.visualizerObj, "location", curFrame)

        # set fcurves of lattice to constant interpolation
        fcurves = self.visualizerObj.animation_data.action.fcurves
        for fcurve in fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'

    @classmethod
    def disable(cls, context):
        """ disables visualizer """
        cls.visualizerObj = bpy.data.groups["AssemblMe_visualizer"].objects[0]
        cls.cancel(cls, context)

    def modal(self, context, event):
        if event.type in {"ESC"}:
            self.report({"INFO"}, "Visualizer disabled")
            context.window_manager.event_timer_remove(self._timer) # remove timer
            self.cancel(context)
            return{"CANCELLED"}

        if event.type == "TIMER":
            scn = context.scene

            try:
                # if the visualizer is has been disabled, stop running modal
                if not groupExists("AssemblMe_visualizer"):
                    return{"CANCELLED"}

                # if new build animation created, update lattice animation
                if self.minAndMax != [props.objMinLoc, props.objMaxLoc]:
                    self.minAndMax = [props.objMinLoc, props.objMaxLoc]
                    self.createAnim()

                # set reference lattice rotation
                if self.visualizerObj.rotation_euler.x != scn.xOrient:
                    self.visualizerObj.rotation_euler.x = scn.xOrient
                if self.visualizerObj.rotation_euler.y != scn.yOrient:
                    self.visualizerObj.rotation_euler.y = scn.yOrient
                if self.visualizerObj.rotation_euler.z != self.zOrient:
                    self.visualizerObj.rotation_euler.z = scn.xOrient * (cos(scn.yOrient) * sin(scn.yOrient))
                    self.zOrient = self.visualizerObj.rotation_euler.z
            except:
                self.handle_exception()

        return{"PASS_THROUGH"}

    def execute(self, context):
        scn = context.scene

        try:
            # if visualizer is enabled, all we need to do is disable it
            if groupExists("AssemblMe_visualizer"):
                self.disable(context)
                return{"FINISHED"}

            # store original_selection and original_active
            self.original_selection = context.selected_objects
            self.original_active = context.active_object

            # alert user that visualizer is running
            self.report({"INFO"}, "Running visualizer... ('ESC' to disable)")

            # add 'LATTICE' object with proper settings
            self.visualizerObj = createVisualizerObject()
            self.layersIdx = list(self.visualizerObj.layers)

            # initialize self.zOrient for modal
            self.zOrient = None

            # test if build animation created
            if groupExists("AssemblMe_all_objects_moved"):
                self.createAnim()
            self.minAndMax = [props.objMinLoc, props.objMaxLoc]

            select(self.original_selection, active=self.original_active)

            # create timer for modal
            wm = context.window_manager
            self._timer = wm.event_timer_add(.02, context.window)
            wm.modal_handler_add(self)
        except:
            self.handle_exception()

        return{"RUNNING_MODAL"}

    def handle_exception(self):
        errormsg = print_exception('AssemblMe_log')
        # if max number of exceptions occur within threshold of time, abort!
        curtime = time.time()
        print('\n'*5)
        print('-'*100)
        print("Something went wrong. Please start an error report with us so we can fix it! (press the 'Report a Bug' button under the 'Advanced' dropdown menu of AssemblMe)")
        print('-'*100)
        print('\n'*5)
        showErrorMessage("Something went wrong. Please start an error report with us so we can fix it! (press the 'Report a Bug' button under the 'Advanced' dropdown menu of AssemblMe)", wrap=240)

    def cancel(self, context):
        scn = context.scene
        # go to layer with visualizer object
        activeLayers = list(scn.layers)
        scn.layers = list(self.visualizerObj.layers)

        # store original_selection and original_active
        self.original_selection = context.selected_objects
        self.original_active = context.active_object

        # delete latticeRef
        self.visualizerObj.hide_select = False
        delete(self.visualizerObj)

        # delete visualizer group
        bpy.data.groups.remove(bpy.data.groups["AssemblMe_visualizer"], do_unlink=True)

        # select original_selection and original_active
        select(self.original_selection, active=self.original_active)

        # reset to original active layers
        scn.layers = activeLayers
