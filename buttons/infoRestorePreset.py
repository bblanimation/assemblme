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

class infoRestorePreset(bpy.types.Operator):
    """Clear animation from objects moved in last 'Create Build Animation' action""" # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.info_restore_preset"                                     # unique identifier for buttons and menu items to reference.
    bl_label = "Info Restore Preset"                                                     # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    # @classmethod
    # def poll(cls, context):
    #     """ ensures operator can execute (if not, returns false) """
    #     return True

    def execute(self, context):
        try:
            txt = bpy.data.texts.new("INFO: Restoring Removed Presets")
            txt.write("\nFollow these steps to restore a removed preset:")
            txt.write("\n\n- Navigate to the AssemblMe folder in your Blender Addons directory")
            txt.write("\n(e.g. ~/Library/Application Support/Blender/2.78c/scripts/addons/assemblme)")
            txt.write("\n- From this directory, navigate to 'lib/presets/backups'")
            txt.write("\n- Select and copy the preset files you would like to restore")
            txt.write("\n- Paste the copied preset files into the parent directory 'lib/presets'")
            txt.write("\n\nThat should do it! If this doesn't work for you, be sure to open up an")
            txt.write("\nissue at 'https://github.com/bblanimation/assemblme/issues' to let us know")
            txt.write("\nwhat steps you took and what problem you've run into so we can fix it ASAP!")
            changeContext(context, 'TEXT_EDITOR')
            for area in bpy.context.window.screen.areas:
                if area.type == 'TEXT_EDITOR':
                    area.spaces.active.text = txt
            bpy.ops.text.jump(line=1)
            bpy.ops.text.move(type='LINE_BEGIN')

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
