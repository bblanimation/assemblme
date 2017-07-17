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

    @classmethod
    def getPresetTuples(cls, fileNames=None):
        # get list of filenames in presets directory
        if not fileNames:
            path = props.addon_prefs.presetsFilepath
            fileNames = os.listdir(path)
        # refresh preset names
        fileNames.sort()
        presetNames = []
        for i in range(len(fileNames)):
            if fileNames[i][-3:] == ".py" and fileNames[i][0] != ".":
                n = fileNames[i][:-3]
                if n != "None" and n != "__init__":
                    presetNames.append((n, n, "Select this preset!")) # get rid of the '.py' at the end of the file name
        presetNames.append(("None", "None", "Don't use a preset"))
        return presetNames

    def writeNewPreset(self, presetName):
        scn = bpy.context.scene
        presetsFilepath = props.addon_prefs.presetsFilepath
        if not os.path.exists(presetsFilepath):
            os.makedirs(presetsFilepath)
        newPresetPath = os.path.join(presetsFilepath, presetName + ".py")
        f = open(newPresetPath, "w")
        f.write("import bpy")
        f.write("\ndef execute():")
        f.write("\n    scn = bpy.context.scene")
        f.write("\n    scn.buildSpeed = " + str(scn.buildSpeed))
        f.write("\n    scn.objectVelocity = " + str(scn.objectVelocity))
        f.write("\n    scn.xLocOffset = " + str(scn.xLocOffset))
        f.write("\n    scn.yLocOffset = " + str(scn.yLocOffset))
        f.write("\n    scn.zLocOffset = " + str(scn.zLocOffset))
        f.write("\n    scn.locInterpolationMode = '" + scn.locInterpolationMode + "'")
        f.write("\n    scn.locationRandom = " + str(scn.locationRandom))
        f.write("\n    scn.xRotOffset = " + str(scn.xRotOffset))
        f.write("\n    scn.yRotOffset = " + str(scn.yRotOffset))
        f.write("\n    scn.zRotOffset = " + str(scn.zRotOffset))
        f.write("\n    scn.rotInterpolationMode = '" + scn.rotInterpolationMode + "'")
        f.write("\n    scn.rotationRandom = " + str(scn.rotationRandom))
        f.write("\n    scn.xOrient = " + str(scn.xOrient))
        f.write("\n    scn.yOrient = " + str(scn.yOrient))
        f.write("\n    scn.orientRandom = " + str(scn.orientRandom))
        f.write("\n    scn.layerHeight = " + str(scn.layerHeight))
        f.write("\n    scn.buildType = '" + scn.buildType + "'")
        f.write("\n    scn.invertBuild = " + str(scn.invertBuild))
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
            elif scn.animPresetToDelete == "Standard Build" or scn.animPresetToDelete == "Explode":
                self.report({"WARNING"}, "Cannot delete default plugins")
                return False
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
                selectedPreset = scn.newPresetName
                scn.newPresetName = ""
                self.report({"INFO"}, "Successfully added new preset '" + scn.newPresetName + "'")
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

            presetNames = self.getPresetTuples(fileNames)

            bpy.types.Scene.animPreset = bpy.props.EnumProperty(
                name="Presets",
                description="Stored AssemblMe presets",
                items=presetNames,
                update=updateAnimPreset,
                default=selectedPreset)

            bpy.types.Scene.animPresetToDelete = bpy.props.EnumProperty(
                name="Preset to Delete",
                description="Another list of stored AssemblMe presets",
                items=presetNames,
                default="None")
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
