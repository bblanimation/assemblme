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
import time
from ..functions import *
props = bpy.props

class createBuildAnimation(bpy.types.Operator):
    """Select objects layer by layer and shift by given values"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.create_build_animation"                                  # unique identifier for buttons and menu items to reference.
    bl_label = "Create Build Animation"                                         # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    def isValid(self):
        """ ensures operator can execute (if not, reports error) """

        scn = bpy.context.scene
        # make sure some objects are selected
        if len(bpy.context.selected_objects) == 0:
            self.report({"WARNING"}, "No objects selected")
            return False
        # make sure no build animation currently in effect
        elif groupExists("AssemblMe_all_objects_moved"):
            self.report({"WARNING"}, "Build animation already created. To create a new animation, press 'Start Over' and try again.")
            return False
        # else, is valid
        else:
            return True

    def execute(self, context):
        try:
            print("\nRunning 'Create Build Animation' operation")

            # get start time
            startTime = time.time()
            self.curTime = startTime

            # Ensure operator can execute
            if not self.isValid():
                return{"CANCELLED"}

            # save backup of blender file
            if context.scene.autoSaveOnCreateAnim:
                if bpy.data.filepath == '':
                    self.report({"ERROR"}, "Backup file could not be saved - You haven't saved your project yet!")
                    return{"CANCELLED"}
                print("saving backup file...")
                bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath[:-6] + "_backup.blend", copy=True)
                self.report({"INFO"}, "Backup file saved")

            # set up other variables
            print("initializing...")
            scn = context.scene
            self.curFrame = scn.frame_current
            scn.lastLayerVelocity = getObjectVelocity()
            props.objects_to_move = context.selected_objects
            self.original_selection = context.selected_objects
            self.original_active = context.active_object

            # populate props.listZValues
            props.listZValues = getListZValues(props.objects_to_move)

            # set props.objMinLoc and props.objMaxLoc
            setBoundsForVisualizer()

            # calculate how many frames the animation will last (depletes props.listZValues)
            scn.animLength = getAnimLength()

            # set first frame to animate from
            if scn.buildType == "Assemble":
                self.curFrame = scn.firstFrame + scn.animLength
            else:
                self.curFrame = scn.firstFrame

            # set frameWithOrigLoc for 'Start Over' operation
            scn.frameWithOrigLoc = self.curFrame

            # Create 'PLAIN_AXES' object (will be parent for animated objects)
            bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0), rotation=(0, 0, 0))
            # # Set custom orientation with active 'ARROWS' object
            # setOrientation("custom")
            # store that 'PLAIN_AXES' object to a group so it can be put in group later
            axisObj = context.active_object
            select(axisObj)
            bpy.ops.group.create(name="AssemblMe_axis_obj")

            # populate props.listZValues again
            props.listZValues = getListZValues(props.objects_to_move)

            # reset upper and lower bound values
            props.z_upper_bound = None
            props.z_lower_bound = None

            # animate the objects
            print("creating animation...")
            animationReturnDict = animateObjects(props.objects_to_move, self.curFrame, scn.locInterpolationMode, scn.rotInterpolationMode)

            # verify animateObjects() ran correctly
            if animationReturnDict["errorMsg"] == None:
                props.objects_to_move = []
            else:
                self.report({"ERROR"}, animationReturnDict["errorMsg"])
                return{"CANCELLED"}

            # handle case where no object was ever selected (e.g. only camera passed to function).
            if scn.frameWithOrigLoc == animationReturnDict["lastFrame"]:
                ignoredTypes = str(props.ignoredTypes).replace("[","").replace("]","")
                self.report({"WARNING"}, "No valid objects selected! (igored types: {})".format(ignoredTypes))
                delete(axisObj)
                select(self.original_selection, active=self.original_active)
                return{"FINISHED"}

            # select all objects moved and put in group
            select(list(animationReturnDict["moved"]))
            bpy.ops.group.create(name="AssemblMe_all_objects_moved")

            # reset upper and lower bound values
            props.z_upper_bound = None
            props.z_lower_bound = None

            # set 'PLAIN_AXES' as active (and selected) object
            select(axisObj, active=axisObj)
            bpy.ops.group.create(name="AssemblMe_axis_obj")

            # set current frame to first frame of animation
            bpy.context.scene.frame_set(scn.firstFrame)

            # STOPWATCH CHECK
            stopWatch("Time Elapsed", time.time()-startTime)
        except:
            self.handle_exception()
            return{"CANCELLED"}

        return{"FINISHED"}

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
