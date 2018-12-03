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

# System imports
import time

# Blender imports
import bpy
from bpy.props import *
props = bpy.props

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
            handle_exception()
            return{"CANCELLED"}
        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        scn, ag = getActiveContextInfo()
        self.objects_to_move = [obj for obj in bpy.data.collections[ag.collection_name].objects if not ag.meshOnly or obj.type == "MESH"]

    ###################################################
    # class variables

    action: EnumProperty(
        items=(
            ("CREATE", "Create", ""),
            ("UPDATE", "Update", ""),
            ("GET_LEN", "Get Length", ""),
        )
    )

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
        origColl = bpy.data.collections[ag.collection_name]
        self.origFrame = scn.frame_current
        if self.action == "UPDATE":
            # set current_frame to animation start frame
            scn.frame_set(ag.frameWithOrigLoc)
        # clear animation data from all objects in animation collection
        clearAnimation(origColl.objects)

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
        if ag.collection_name == "":
            self.report({"WARNING"}, "No collection name specified")
            return False
        if not collExists(ag.collection_name):
            self.report({"WARNING"}, "Collection '%(n)s' does not exist." % locals())
            return False
        if len(bpy.data.collections[ag.collection_name].objects) == 0:
            self.report({"WARNING"}, "Collection contains no objects!")
            return False
        # make sure no objects in this collection are part of another AssemblMe animation
        for i in range(len(scn.aglist)):
            if i == scn.aglist_index or not scn.aglist[i].animated:
                continue
            g = bpy.data.collections.get(scn.aglist[i].collection_name)
            for obj in self.objects_to_move:
                if g in obj.users_collection:
                    self.report({"ERROR"}, "Some objects in this collection are part of another AssemblMe animation")
                    return False
        return True

    #############################################
