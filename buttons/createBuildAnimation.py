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
from bpy.props import *

# Addon imports
from ..functions import *

class ASSEMBLME_OT_create_build_animation(bpy.types.Operator):
    """Select objects layer by layer and shift by given values"""               # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "assemblme.create_build_animation"                              # unique identifier for buttons and menu items to reference.
    bl_label = "Create Build Animation"                                         # display name in the interface.
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
            self.createAnim()
        except:
            assemblme_handle_exception()
            return{"CANCELLED"}
        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        scn, ag = getActiveContextInfo()
        self.objects_to_move = [obj for obj in ag.group.objects if not ag.meshOnly or obj.type == "MESH"]
        self.action = "CREATE" if not ag.animated else "UPDATE"

    ###################################################
    # class variables

    # NONE!

    ###################################################
    # class methods

    @timed_call("Time Elapsed")
    def createAnim(self):
        print("\ncreating build animation...")
        # initialize vars
        scn, ag = getActiveContextInfo()

        # ensure operation can run
        if not self.isValid(scn, ag):
            return {"CANCELLED"}

        # save backup of blender file
        if self.action == "CREATE":
            saveBackupFile(self)

        # set up other variables
        ag.lastLayerVelocity = getObjectVelocity()
        origGroup = ag.group
        self.origFrame = scn.frame_current
        if self.action == "UPDATE":
            # set current_frame to animation start frame
            scn.frame_set(ag.frameWithOrigLoc)
        # clear animation data from all objects in ag.group
        clearAnimation(origGroup.objects)

        ### BEGIN ANIMATION GENERATION ###
        # populate self.listZValues
        self.listZValues,rotXL,rotYL = getListZValues(self.objects_to_move)

        # set props.objMinLoc and props.objMaxLoc
        setBoundsForVisualizer(self.listZValues)

        # calculate how many frames the animation will last
        ag.animLength = getAnimLength(self.objects_to_move, self.listZValues.copy(), ag.layerHeight, ag.invertBuild, ag.skipEmptySelections)

        # set first frame to animate from
        self.curFrame = ag.firstFrame + (ag.animLength if ag.buildType == "Assemble" else 0)

        # set frameWithOrigLoc for 'Start Over' operation
        ag.frameWithOrigLoc = self.curFrame

        # reset upper and lower bound values
        props.z_upper_bound = None
        props.z_lower_bound = None

        # animate the objects
        animationReturnDict = animateObjects(self.objects_to_move, self.listZValues, self.curFrame, ag.locInterpolationMode, ag.rotInterpolationMode)

        # verify animateObjects() ran correctly
        if animationReturnDict["errorMsg"] != None:
            self.report({"ERROR"}, animationReturnDict["errorMsg"])
            return{"CANCELLED"}

        # handle case where no object was ever selected (e.g. only camera passed to function).
        if self.action == "CREATE" and ag.frameWithOrigLoc == animationReturnDict["lastFrame"]:
            warningMsg = "No valid objects selected!"
            if ag.meshOnly:
                warningMsg += " (Non-mesh objects ignored – see advanced settings)"
            self.report({"WARNING"}, warningMsg)
            return{"FINISHED"}

        # reset upper and lower bound values
        props.z_upper_bound = None
        props.z_lower_bound = None

        # set current_frame to original current_frame
        bpy.context.scene.frame_set(self.origFrame)
        if self.action == "CREATE":
            disableRelationshipLines()
            ag.animated = True

    def isValid(self, scn, ag):
        if ag.group is None:
            self.report({"WARNING"}, "No group name specified")
            return False
        if len(ag.group.objects) == 0:
            self.report({"WARNING"}, "Group contains no objects!")
            return False
        # make sure no objects in this group are part of another AssemblMe animation
        for i in range(len(scn.aglist)):
            if i == scn.aglist_index or not scn.aglist[i].animated:
                continue
            g = scn.aglist[i].group
            for obj in self.objects_to_move:
                if g in obj.users_group:
                    self.report({"ERROR"}, "Some objects in this group are part of another AssemblMe animation")
                    return False
        return True

    #############################################
