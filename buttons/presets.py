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

class animPresets(bpy.types.Operator):
    """Create new preset with current animation settings"""                     # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.animation_presets"                                       # unique identifier for buttons and menu items to reference.
    bl_label = "Animation Presets"                                              # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    # @classmethod
    # def poll(cls, context):
    #     """ ensures operator can execute (if not, returns false) """
    #     if context.scene.newPresetName != "":
    #         return True
    #     return False
    #
    action = bpy.props.EnumProperty(
        items=(
            ('CREATE', "Create", ""),
            ('REMOVE', "Remove", ""),
        )
    )

    def writeNewPreset(self, presetName):
        scn = bpy.context.scene
        ag = scn.aglist[scn.aglist_index]
        presetsFilepath = props.addon_prefs.presetsFilepath
        if not os.path.exists(presetsFilepath):
            os.makedirs(presetsFilepath)
        newPresetPath = os.path.join(presetsFilepath, presetName + ".py")
        f = open(newPresetPath, "w")
        f.write("import bpy")
        f.write("\ndef execute():")
        f.write("\n    scn = bpy.context.scene")
        f.write("\n    ag = scn.aglist[scn.aglist_index]")
        f.write("\n    ag.buildSpeed = " + str(ag.buildSpeed))
        f.write("\n    ag.velocity = " + str(round(ag.velocity, 6)))
        f.write("\n    ag.xLocOffset = " + str(round(ag.xLocOffset, 6)))
        f.write("\n    ag.yLocOffset = " + str(round(ag.yLocOffset, 6)))
        f.write("\n    ag.zLocOffset = " + str(round(ag.zLocOffset, 6)))
        f.write("\n    ag.locInterpolationMode = '" + ag.locInterpolationMode + "'")
        f.write("\n    ag.locationRandom = " + str(round(ag.locationRandom, 6)))
        f.write("\n    ag.xRotOffset = " + str(ag.xRotOffset))
        f.write("\n    ag.yRotOffset = " + str(ag.yRotOffset))
        f.write("\n    ag.zRotOffset = " + str(ag.zRotOffset))
        f.write("\n    ag.rotInterpolationMode = '" + ag.rotInterpolationMode + "'")
        f.write("\n    ag.rotationRandom = " + str(round(ag.rotationRandom, 6)))
        f.write("\n    ag.xOrient = " + str(round(ag.xOrient, 6)))
        f.write("\n    ag.yOrient = " + str(round(ag.yOrient, 6)))
        f.write("\n    ag.orientRandom = " + str(round(ag.orientRandom, 6)))
        f.write("\n    ag.layerHeight = " + str(round(ag.layerHeight, 6)))
        f.write("\n    ag.buildType = '" + ag.buildType + "'")
        f.write("\n    ag.invertBuild = " + str(round(ag.invertBuild, 6)))
        f.write("\n    return None")

    def canRun(self):
        scn = bpy.context.scene
        if self.action == "CREATE":
            if scn.newPresetName == "":
                self.report({"WARNING"}, "No preset name specified")
                return False
        if self.action == "REMOVE":
            if scn.animPresetToDelete == "None":
                self.report({"WARNING"}, "No preset name specified")
                return False
            # # prevent users from deleting default presets
            # elif scn.animPresetToDelete in scn.assemblme_default_presets:
            #     self.report({"WARNING"}, "Cannot delete default p")
            #     return False
        return True

    def execute(self, context):
        if not self.canRun():
            return{"CANCELLED"}
        try:
            scn = bpy.context.scene
            path = props.addon_prefs.presetsFilepath
            fileNames = os.listdir(path)
            selectedPreset = "None"
            if self.action == "CREATE":
                if scn.newPresetName + ".py" in fileNames:
                    self.report({"WARNING"}, "Preset already exists with this name. Try another name!")
                    return{"CANCELLED"}
                # write new preset to file
                self.writeNewPreset(scn.newPresetName)
                fileNames.append(scn.newPresetName + ".py")
                selectedPreset = str(scn.newPresetName)
                self.report({"INFO"}, "Successfully added new preset '" + scn.newPresetName + "'")
                scn.newPresetName = ""
            elif self.action == "REMOVE":
                backupPath = os.path.join(path, "backups")
                fileName = scn.animPresetToDelete + ".py"
                filePath = os.path.join(path, fileName)
                backupFilePath = os.path.join(backupPath, fileName)
                if os.path.isfile(filePath):
                    if not os.path.exists(backupPath):
                        os.mkdir(backupPath)
                    if os.path.isfile(backupFilePath):
                        os.remove(backupFilePath)
                    os.rename(filePath, backupFilePath)
                    fileNames.remove(scn.animPresetToDelete + ".py")
                    self.report({"INFO"}, "Successfully removed preset '" + scn.animPresetToDelete + "'")
                else:
                    self.report({"WARNING"}, "Preset '" + scn.animPresetToDelete + "' does not exist.")
                    return{"CANCELLED"}

            presetNames = getPresetTuples(fileNames)
            bpy.types.Scene.animPreset = bpy.props.EnumProperty(
                name="Presets",
                description="Stored AssemblMe presets",
                items=presetNames,
                update=updateAnimPreset,
                default="None")
            scn.animPreset = selectedPreset

            bpy.types.Scene.animPresetToDelete = bpy.props.EnumProperty(
                name="Preset to Delete",
                description="Another list of stored AssemblMe presets",
                items=presetNames,
                default="None")
            scn.animPresetToDelete = selectedPreset
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
