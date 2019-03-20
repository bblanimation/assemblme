# Copyright (C) 2018 Christopher Gearhart
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

# Addon imports
from ..functions import *

class ASSEMBLME_OT_start_over(bpy.types.Operator):
    """Clear animation from objects moved in last 'Create Build Animation' action""" # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "assemblme.start_over"                                          # unique identifier for buttons and menu items to reference.
    bl_label = "Start Over"                                                     # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

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
            self.startOver()
        except:
            assemblme_handle_exception()
        return{"FINISHED"}

    ###################################################
    # class methods

    @timed_call("Time Elapsed")
    def startOver(self):
        # initialize vars
        scn, ag = getActiveContextInfo()

        # save backup of blender file if enabled in user prefs
        saveBackupFile(self)

        # set current_frame to animation start frame
        self.origFrame = scn.frame_current
        bpy.context.scene.frame_set(ag.frameWithOrigLoc)

        # clear objMinLoc and objMaxLoc
        props.objMinLoc, props.objMaxLoc = 0, 0

        # clear animation data from all objects in 'AssemblMe_all_objects_moved' group/collection
        if ag.collection is not None:
            print("\nClearing animation data from " + str(len(ag.collection.objects)) + " objects.")
            clearAnimation(ag.collection.objects)

        # set current_frame to original current_frame
        bpy.context.scene.frame_set(self.origFrame)

        ag.animated = False

    #############################################
