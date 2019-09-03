# Copyright (C) 2019 Christopher Gearhart
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
from shutil import copyfile

# Blender imports
import bpy
from bpy.props import EnumProperty

# Module imports
from ..functions import *

class ASSEMBLME_OT_anim_presets(bpy.types.Operator):
    """Create new preset with current animation settings"""
    bl_idname = "assemblme.anim_presets"
    bl_label = "Animation Presets"
    bl_options = {"REGISTER", "UNDO"}

    ################################################
    # Blender Operator methods

    # @classmethod
    # def poll(cls, context):
    #     """ ensures operator can execute (if not, returns false) """
    #     if context.scene.new_preset_name != "":
    #         return True
    #     return False

    def execute(self, context):
        if not self.can_run():
            return{"CANCELLED"}
        try:
            scn = bpy.context.scene
            path = get_addon_preferences().presets_filepath
            filenames = get_filenames(path)
            selected_preset = "None"
            if self.action == "CREATE":
                if scn.new_preset_name + ".py" in filenames:
                    self.report({"WARNING"}, "Preset already exists with this name. Try another name!")
                    return{"CANCELLED"}
                # write new preset to file
                self.write_new_preset(scn.new_preset_name)
                filenames.append(scn.new_preset_name + ".py")
                selected_preset = str(scn.new_preset_name)
                self.report({"INFO"}, "Successfully added new preset '" + scn.new_preset_name + "'")
                scn.new_preset_name = ""
            elif self.action == "REMOVE":
                backup_path = os.path.join(path, "backups")
                filename = scn.anim_preset_to_delete + ".py"
                filepath = os.path.join(path, filename)
                backup_filepath = os.path.join(backup_path, filename)
                if os.path.isfile(filepath):
                    if not os.path.exists(backup_path):
                        os.mkdir(backup_path)
                    if os.path.isfile(backup_filepath):
                        os.remove(backup_filepath)
                    os.rename(filepath, backup_filepath)
                    filenames.remove(scn.anim_preset_to_delete + ".py")
                    self.report({"INFO"}, "Successfully removed preset '" + scn.anim_preset_to_delete + "'")
                else:
                    self.report({"WARNING"}, "Preset '" + scn.anim_preset_to_delete + "' does not exist.")
                    return{"CANCELLED"}

            preset_names = get_preset_tuples(filenames=filenames)
            bpy.types.Scene.anim_preset = EnumProperty(
                name="Presets",
                description="Stored AssemblMe presets",
                items=preset_names,
                update=update_anim_preset,
                default="None")
            scn.anim_preset = selected_preset

            bpy.types.Scene.anim_preset_to_delete = EnumProperty(
                name="Preset to Delete",
                description="Another list of stored AssemblMe presets",
                items=preset_names,
                default="None")
            scn.anim_preset_to_delete = selected_preset
        except:
            assemblme_handle_exception()

        return{"FINISHED"}

    ###################################################
    # class variables

    action = EnumProperty(
        items=(
            ("CREATE", "Create", ""),
            ("REMOVE", "Remove", ""),
        )
    )

    ###################################################
    # class methods

    def write_new_preset(self, presetName):
        scn, ag = get_active_context_info()
        presets_filepath = get_addon_preferences().presets_filepath
        if not os.path.exists(presets_filepath):
            os.makedirs(presets_filepath)
        new_preset_path = os.path.join(presets_filepath, presetName + ".py")
        f = open(new_preset_path, "w")
        f.write("import bpy")
        f.write("\ndef execute():")
        f.write("\n    scn = bpy.context.scene")
        f.write("\n    ag = scn.aglist[scn.aglist_index]")
        f.write("\n    ag.build_speed = " + str(ag.build_speed))
        f.write("\n    ag.velocity = " + str(round(ag.velocity, 6)))
        f.write("\n    ag.loc_offset = " + str(vec_round(ag.loc_offset, 6).to_tuple()))
        f.write("\n    ag.loc_interpolation_mode = '" + ag.loc_interpolation_mode + "'")
        f.write("\n    ag.loc_random = " + str(round(ag.loc_random, 6)))
        f.write("\n    ag.rot_offset = " + str(tuple(ag.rot_offset)))
        f.write("\n    ag.rot_interpolation_mode = '" + ag.rot_interpolation_mode + "'")
        f.write("\n    ag.rot_random = " + str(round(ag.rot_random, 6)))
        f.write("\n    ag.orient = " + str(tuple(vec_round(ag.orient, 6))))
        f.write("\n    ag.orient_random = " + str(round(ag.orient_random, 6)))
        f.write("\n    ag.layer_height = " + str(round(ag.layer_height, 6)))
        f.write("\n    ag.build_type = '" + ag.build_type + "'")
        f.write("\n    ag.inverted_build = " + str(round(ag.inverted_build, 6)))
        f.write("\n    ag.skip_empty_selections = " + str(ag.skip_empty_selections))
        f.write("\n    ag.use_global = " + str(ag.use_global))
        f.write("\n    ag.mesh_only = " + str(ag.mesh_only))
        f.write("\n    return None")

    def can_run(self):
        scn = bpy.context.scene
        if self.action == "CREATE":
            if scn.new_preset_name == "":
                self.report({"WARNING"}, "No preset name specified")
                return False
        if self.action == "REMOVE":
            if scn.anim_preset_to_delete == "None":
                self.report({"WARNING"}, "No preset name specified")
                return False
            # # prevent users from deleting default presets
            # elif scn.anim_preset_to_delete in scn.assemblme_default_presets:
            #     self.report({"WARNING"}, "Cannot delete default p")
            #     return False
        return True

    #############################################
