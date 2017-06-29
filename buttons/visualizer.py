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
import bmesh
from ..functions import *
props = bpy.props

class visualizer(bpy.types.Operator):
    """Visualize the layer orientation with a plane"""                          # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.visualize_layer_orientation"                             # unique identifier for buttons and menu items to reference.
    bl_label = "Visualize Layer Orientation"                                    # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    def __init__(self):
        """ sets up self.visualizerObj """
        if groupExists("AssemblMe_visualizer"):
            # set self.visualizer and self.m with existing data
            self.visualizerObj = bpy.data.groups["AssemblMe_visualizer"].objects[0]
            self.m = self.visualizerObj.data
        else:
            # create visualizer object
            self.m = bpy.data.meshes.new('AssemblMe_visualizer_m')
            self.visualizerObj = bpy.data.objects.new('assemblMe_visualizer', self.m)
            self.visualizerObj.hide_select = True
            self.visualizerObj.hide_render = True
            # put in new group
            bpy.ops.group.create(name="AssemblMe_visualizer")
            bpy.data.groups["AssemblMe_visualizer"].objects.link(self.visualizerObj)
        # not sure what this does, to be honest
        visualizer.instance = self

    def createAnim(self):
        scn = bpy.context.scene
        # if first and last location are the same, keep visualizer stationary
        if props.objMinLoc == props.objMaxLoc:
            self.visualizerObj.animation_data_clear()
            if type(props.objMinLoc) == type(self.visualizerObj.location):
                self.visualizerObj.location = props.objMinLoc
            else:
                self.visualizerObj.location = (0,0,0)
            return "static"
        # else, create animation
        else:
            # set up vars
            self.visualizerObj.location = props.objMinLoc
            curFrame = scn.frameWithOrigLoc
            idx = -1
            # insert keyframe and iterate current frame, and set another
            insertKeyframes(self.visualizerObj, "location", curFrame, 'LINEAR', idx)
            self.visualizerObj.location = props.objMaxLoc
            if scn.buildType == "Assemble":
                curFrame -= (scn.animLength - scn.lastLayerVelocity)
                idx -= 1
            else:
                curFrame += (scn.animLength - scn.lastLayerVelocity)
            insertKeyframes(self.visualizerObj, "location", curFrame, 'LINEAR', idx)
            return "animated"

    def enable(self, context):
        """ enables visualizer """
        scn = context.scene
        # alert user that visualizer is enabled
        self.report({"INFO"}, "Visualizer enabled... ('ESC' to disable)")
        # add proper mesh data to visualizer object
        visualizerBM = makeSimple2DLattice(scn.visualizerNumCuts, scn.visualizerScale)
        visualizerBM.to_mesh(self.visualizerObj.data)
        # link visualizer object to scene
        scn.objects.link(self.visualizerObj)
        scn.visualizerLinked = True

    def disable(self, context):
        """ disables visualizer """
        # alert user that visualizer is disabled
        self.report({"INFO"}, "Visualizer disabled")
        # unlink visualizer object to scene
        context.scene.objects.unlink(self.visualizerObj)
        context.scene.visualizerLinked = False

    @staticmethod
    def enabled():
        """ returns boolean for visualizer linked to scene """
        return bpy.context.scene.visualizerLinked

    def modal(self, context, event):
        """ runs as long as visualizer is active """
        if event.type in {"ESC"}:
            self.report({"INFO"}, "Visualizer disabled")
            self.disable(context)
            return{"CANCELLED"}

        if event.type == "TIMER":
            scn = context.scene
            try:
                # if the visualizer is has been disabled, stop running modal
                if not self.enabled():
                    return{"CANCELLED"}
                # if new build animation created, update visualizer animation
                if self.minAndMax != [props.objMinLoc, props.objMaxLoc]:
                    self.minAndMax = [props.objMinLoc, props.objMaxLoc]
                    self.createAnim()
                # set visualizer object rotation
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
            # if enabled, all we do is disable it
            if self.enabled():
                self.disable(context)
                return{"FINISHED"}
            else:
                # enable visualizer
                self.enable(context)
                # create animation for visualizer if build animation exists
                if groupExists("AssemblMe_all_objects_moved"):
                    self.createAnim()
                self.minAndMax = [props.objMinLoc, props.objMaxLoc]
                # initialize self.zOrient for modal
                self.zOrient = None
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
        # remove timer
        context.window_manager.event_timer_remove(self._timer)
        # delete visualizer object and mesh
        bpy.data.objects.remove(self.visualizerObj, True)
        bpy.data.meshes.remove(self.m, True)
        # remove visualizer group
        if groupExists("AssemblMe_visualizer"):
            vGroup = bpy.data.groups["AssemblMe_visualizer"]
            bpy.data.groups.remove(vGroup, do_unlink=True)
