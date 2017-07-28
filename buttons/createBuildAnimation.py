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

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        return True

    action = bpy.props.EnumProperty(
        items=(
            ("CREATE", "Create", ""),
            ("UPDATE", "Update", ""),
            ("GET_LEN", "Get Length", ""),
        )
    )

    def execute(self, context):
        try:
            print("\nRunning 'Create Build Animation' operation")

            # get start time
            startTime = time.time()
            self.curTime = startTime

            scn = context.scene
            ag = scn.aglist[scn.aglist_index]

            if ag.group_name == "":
                self.report({"WARNING"}, "No group name specified")
                return {"CANCELLED"}
            if not groupExists(ag.group_name):
                self.report({"WARNING"}, "Group '%(n)s' does not exist." % locals())
                return {"CANCELLED"}
            if len(bpy.data.groups[ag.group_name].objects) == 0:
                self.report({"WARNING"}, "Group contains no objects!")
                return {"CANCELLED"}

            # save backup of blender file
            if context.scene.autoSaveOnCreateAnim and self.action == "CREATE":
                if bpy.data.filepath == '':
                    self.report({"ERROR"}, "Backup file could not be saved - You haven't saved your project yet!")
                    return{"CANCELLED"}
                print("saving backup file...")
                bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath[:-6] + "_backup.blend", copy=True)
                self.report({"INFO"}, "Backup file saved")

            # set up other variables
            print("initializing...")
            self.curFrame = scn.frame_current
            ag.lastLayerVelocity = getObjectVelocity()
            self.original_selection = context.selected_objects
            self.original_active = context.active_object
            origGroup = bpy.data.groups[ag.group_name]
            # set up origGroup variable
            self.objects_to_move = list(bpy.data.groups[ag.group_name].objects)
            if self.action == "UPDATE":
                # set current_frame to animation start frame
                self.origFrame = scn.frame_current
                bpy.context.scene.frame_set(ag.frameWithOrigLoc)
                # clear animation data from all objects in ag.group_name group
                for obj in origGroup.objects:
                    obj.animation_data_clear()
                # set up other variables
                self.objects_moved = []

            # make sure no objects in this group are part of another AssemblMe animation
            for obj in self.objects_to_move:
                for i in range(len(scn.aglist)):
                    if i != scn.aglist_index:
                        ag0 = scn.aglist[i]
                        if ag0.animated:
                            g = bpy.data.groups.get(ag0.group_name)
                            if g in obj.users_group:
                                self.report({"ERROR"}, "Some objects in this group are part of another AssemblMe animation")
                                return{"CANCELLED"}

            # NOTE: This was commented out for the sake of performance
            # set origin to center of mass for selected objects
            # setOrigin(self.objects_to_move, 'ORIGIN_CENTER_OF_MASS')

            ### BEGIN ANIMATION GENERATION ###
            # populate self.listZValues
            self.listZValues,rotXL,rotYL = getListZValues(self.objects_to_move)

            # set props.objMinLoc and props.objMaxLoc
            setBoundsForVisualizer(self.listZValues)

            # calculate how many frames the animation will last (depletes self.listZValues)
            ag.animLength = getAnimLength(self.objects_to_move, self.listZValues)

            # set first frame to animate from
            if ag.buildType == "Assemble":
                self.curFrame = ag.firstFrame + ag.animLength
            else:
                self.curFrame = ag.firstFrame

            # set frameWithOrigLoc for 'Start Over' operation
            ag.frameWithOrigLoc = self.curFrame

            # if self.action == "CREATE":
            #     # Create 'PLAIN_AXES' object (will be parent for animated objects)
            #     bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0), rotation=(0, 0, 0))
            #     # # Set custom orientation with active 'ARROWS' object
            #     # setOrientation("custom")
            #     # store that 'PLAIN_AXES' object to a group so it can be put in group later
            #     axisObj = context.active_object
            #     aoGroup = bpy.data.groups.new("AssemblMe_axis_obj")
            #     aoGroup.objects.link(axisObj)

            # populate self.listZValues again
            self.listZValues,_,_ = getListZValues(self.objects_to_move, rotXL, rotYL)

            # reset upper and lower bound values
            props.z_upper_bound = None
            props.z_lower_bound = None

            # animate the objects
            print("creating animation...")
            animationReturnDict = animateObjects(self.objects_to_move, self.listZValues, self.curFrame, ag.locInterpolationMode, ag.rotInterpolationMode)

            # verify animateObjects() ran correctly
            if animationReturnDict["errorMsg"] != None:
                self.report({"ERROR"}, animationReturnDict["errorMsg"])
                return{"CANCELLED"}

            if self.action == "CREATE":
                # handle case where no object was ever selected (e.g. only camera passed to function).
                if ag.frameWithOrigLoc == animationReturnDict["lastFrame"]:
                    ignoredTypes = str(props.ignoredTypes).replace("[","").replace("]","")
                    self.report({"WARNING"}, "No valid objects selected! (igored types: {})".format(ignoredTypes))
                    return{"FINISHED"}

                # select all objects moved and put in group
                select(list(animationReturnDict["moved"]))

            # reset upper and lower bound values
            props.z_upper_bound = None
            props.z_lower_bound = None

            # set to original selection and active object
            select(self.original_selection, active=self.original_active)
            if self.action == "UPDATE":
                # set current_frame to original current_frame
                bpy.context.scene.frame_set(self.origFrame)
            elif self.action == "CREATE":
                # set current frame to first frame of animation
                bpy.context.scene.frame_set(ag.firstFrame)
                disableRelationshipLines()
                ag.animated = True

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
