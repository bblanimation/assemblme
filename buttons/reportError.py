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
import os

# Blender imports
import bpy
props = bpy.props

# Addon imports
from ..functions import *

class ASSEMBLME_OT_report_error(bpy.types.Operator):
    """Report a bug via an automatically generated issue ticket"""              # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "assemblme.report_error"                                        # unique identifier for buttons and menu items to reference.
    bl_label = "Report Error"                                                   # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    def execute(self, context):
        # set up file paths
        libraryServersPath = os.path.join(getLibraryPath(), "error_log")
        # write necessary debugging information to text file
        writeErrorToFile(libraryServersPath, 'AssemblMe_log', props.assemblme_version)
        # open error report in UI with text editor
        lastType = changeContext(context, "TEXT_EDITOR")
        try:
            bpy.ops.text.open(filepath=os.path.join(libraryServersPath, "AssemblMe_error_report.txt"))
            bpy.context.space_data.show_word_wrap = True
            self.report({"INFO"}, "Opened 'AssemblMe_error_report.txt'")
            bpy.props.needsUpdating = True
        except:
            changeContext(context, lastType)
            self.report({"ERROR"}, "ERROR: Could not open 'AssemblMe_error_report.txt'. If the problem persists, try reinstalling the add-on.")
        return{"FINISHED"}

    #############################################

class ASSEMBLME_OT_close_report_error(bpy.types.Operator):
    """Deletes error report from blender's memory (still exists in file system)"""    # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "assemblme.close_report_error"                                        # unique identifier for buttons and menu items to reference.
    bl_label = "Close Report Error"                                                   # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    def execute(self, context):
        txt = bpy.data.texts['AssemblMe_log']
        bpy.data.texts.remove(txt, True)
        return{"FINISHED"}

    #############################################
