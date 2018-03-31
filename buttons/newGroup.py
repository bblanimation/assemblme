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

class newGroupFromSelection(bpy.types.Operator):
    """Create new group containing selected objects, and set as group to assemble""" # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.new_group_from_selection"                                # unique identifier for buttons and menu items to reference.
    bl_label = "New Group"                                                      # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        return True
    #
    # action = bpy.props.EnumProperty(
    #     items=(
    #         ('CREATE', "Create", ""),
    #         ('REMOVE', "Remove", ""),
    #     )
    # )
    def canRun(self):
        if len(bpy.context.selected_objects) == 0:
            self.report({"WARNING"}, "No objects selected")
            return False
        return True

    def execute(self, context):
        if not self.canRun():
            return{"CANCELLED"}
        try:
            scn = bpy.context.scene
            ag = scn.aglist[scn.aglist_index]
            i = 0
            groupIdx = 0
            while groupIdx != -1:
                i += 1
                groupIdx = bpy.data.groups.find("AssemblMe_animated_group_%(i)s" % locals())
            agGroup = bpy.data.groups.new("AssemblMe_animated_group_%(i)s" % locals())
            for obj in bpy.context.selected_objects:
                agGroup.objects.link(obj)
            ag.group_name = agGroup.name
        except:
            handle_exception()

        return{"FINISHED"}
