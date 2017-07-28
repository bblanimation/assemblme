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

class startOver(bpy.types.Operator):
    """Clear animation from objects moved in last 'Create Build Animation' action""" # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.start_over"                                              # unique identifier for buttons and menu items to reference.
    bl_label = "Start Over"                                                     # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        ag = scn.aglist[scn.aglist_index]
        if ag.animated:
            return True
        return False

    def execute(self, context):
        try:
            # get start time
            startTime = time.time()

            # set up origGroup variable
            scn = context.scene
            ag = scn.aglist[scn.aglist_index]
            origGroup = bpy.data.groups[ag.group_name]
            # aoGroup = bpy.data.groups["AssemblMe_axis_obj"]

            # save backup of blender file
            if scn.autoSaveOnStartOver:
                if bpy.data.filepath == '':
                    self.report({"ERROR"}, "Backup file could not be saved - You haven't saved your project yet!")
                    return{"CANCELLED"}
                bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath[:-6] + "_backup.blend", copy=True)
                self.report({"INFO"}, "Backup file saved")

            # set current_frame to animation start frame
            self.origFrame = scn.frame_current
            bpy.context.scene.frame_set(ag.frameWithOrigLoc)

            print("\nClearing animation data from " + str(len(origGroup.objects)) + " objects.")

            # clear objMinLoc and objMaxLoc
            props.objMinLoc = 0
            props.objMaxLoc = 0

            # # delete axis reference object
            # if groupExists("AssemblMe_axis_obj"):
            #     delete(aoGroup.objects[0])
            # # remove axis obj group
            # bpy.data.groups.remove(aoGroup, True)

            # clear animation data from all objects in 'AssemblMe_all_objects_moved' group
            for obj in origGroup.objects:
                obj.animation_data_clear()
            select(list(origGroup.objects))

            if "AssemblMe_animated_group_" in ag.group_name:
                bpy.data.groups.remove(origGroup, True)
                ag.group_name = ""

            # set current_frame to original current_frame
            bpy.context.scene.frame_set(self.origFrame)

            ag.animated = False

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
