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

class updateBuildAnimation(bpy.types.Operator):
    """Select objects layer by layer and shift by given values"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.update_build_animation"                                  # unique identifier for buttons and menu items to reference.
    bl_label = "Update Build Animation"                                         # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        if not groupExists("AssemblMe_all_objects_moved"):
            return False
        return True

    def execute(self, context):
        try:
            print("\nRunning 'Create Build Animation' operation")

            # get start time
            startTime = time.time()
            self.curTime = startTime

            # get original selection and active obj
            self.original_selection = context.selected_objects
            self.original_active = context.active_object

            # set up aomGroup variable
            scn = context.scene
            aomGroup = bpy.data.groups["AssemblMe_all_objects_moved"]

            # set current_frame to animation start frame
            self.origFrame = scn.frame_current
            bpy.context.scene.frame_set(scn.frameWithOrigLoc)

            # clear animation data from all objects in 'AssemblMe_all_objects_moved' group
            for obj in aomGroup.objects:
                obj.animation_data_clear()

            ### BEGIN ANIMATION GENERATION ###
            # set up other variables
            scn.lastLayerVelocity = getObjectVelocity()
            self.objects_moved = []
            props.objects_to_move = list(aomGroup.objects)

            # populate props.listZValues
            props.listZValues,rotXL,rotYL = getListZValues(props.objects_to_move)

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

            # populate props.listZValues again
            props.listZValues,_,_ = getListZValues(props.objects_to_move, rotXL, rotYL)

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

            # reset upper and lower bound values
            props.z_upper_bound = None
            props.z_lower_bound = None

            # set to original selection and active object
            select(self.original_selection, active=self.original_active)

            # set current_frame to original current_frame
            bpy.context.scene.frame_set(self.origFrame)

            # STOPWATCH CHECK
            stopWatch("Time Elapsed", time.time()-startTime)
        except:
            self.handle_exception()

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
