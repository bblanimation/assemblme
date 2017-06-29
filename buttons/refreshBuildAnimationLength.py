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
from ..functions import *
props = bpy.props

class refreshBuildAnimationLength(bpy.types.Operator):
    """Refreshes the box in UI with build animation length"""                   # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.refresh_build_animation_length"                          # unique identifier for buttons and menu items to reference.
    bl_label = "Refresh Build Animation Length"                                 # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        if not groupExists("AssemblMe_all_objects_moved"):
            return 0 < len([
                o for o in context.selected_objects if
                    o.type not in props.ignoredTypes                            # object not of ignored type
                ])
        return True

    def execute(self, context):
        try:
            # set up variables
            scn = context.scene

            if groupExists("AssemblMe_all_objects_moved"):
                # if objects in 'AssemblMe_all_objects_moved', populate objects_to_move with them
                props.objects_to_move = bpy.data.groups["AssemblMe_all_objects_moved"].objects
                # set current_frame to animation start frame
                self.origFrame = scn.frame_current
                bpy.context.scene.frame_set(scn.frameWithOrigLoc)
            else:
                # else, populate objects_to_move with selected_objects
                props.objects_to_move = context.selected_objects

            # populate props.listZValues
            props.listZValues = getListZValues(props.objects_to_move)

            # set props.objMinLoc and props.objMaxLoc
            setBoundsForVisualizer()

            # calculate how many frames the animation will last (depletes props.listZValues)
            scn.animLength = getAnimLength()

            if groupExists("AssemblMe_all_objects_moved"):
                # set current_frame to original current_frame
                bpy.context.scene.frame_set(self.origFrame)

            # reset upper and lower bound values
            props.z_upper_bound = None
            props.z_lower_bound = None
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
