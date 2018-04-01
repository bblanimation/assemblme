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
import random
import sys
import time
import os
import traceback
from math import *

# Blender imports
import bpy
props = bpy.props

# Addon imports
from .common import *
# from .common_mesh_generate import *

def getActiveContextInfo(ag_idx=None):
    scn = bpy.context.scene
    ag_idx = ag_idx or scn.aglist_index
    ag = scn.aglist[ag_idx]
    return scn, ag

def saveBackupFile(self):
    if bpy.context.user_preferences.addons[bpy.props.assemblme_module_name].preferences.autoSaveOnStartOver:
        if bpy.data.filepath == '':
            self.report({"ERROR"}, "Backup file could not be saved - You haven't saved your project yet!")
            return{"CANCELLED"}
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath[:-6] + "_backup.blend", copy=True)
        self.report({"INFO"}, "Backup file saved")

def getRandomizedOrient(orient):
    """ returns randomized orientation based on user settings """
    scn, ag = getActiveContextInfo()
    return (orient + random.uniform(-ag.orientRandom, ag.orientRandom))

def getOffsetLocation(location):
    """ returns randomized location offset """
    scn, ag = getActiveContextInfo()
    X = location.x + random.uniform(-ag.locationRandom, ag.locationRandom) + ag.xLocOffset
    Y = location.y + random.uniform(-ag.locationRandom, ag.locationRandom) + ag.yLocOffset
    Z = location.z + random.uniform(-ag.locationRandom, ag.locationRandom) + ag.zLocOffset
    return (X, Y, Z)

def getOffsetRotation(rotation):
    """ returns randomized rotation offset """
    scn, ag = getActiveContextInfo()
    X = rotation.x + random.uniform(-ag.rotationRandom, ag.rotationRandom) + ag.xRotOffset
    Y = rotation.y + random.uniform(-ag.rotationRandom, ag.rotationRandom) + ag.yRotOffset
    Z = rotation.z + random.uniform(-ag.rotationRandom, ag.rotationRandom) + ag.zRotOffset
    return Vector((X, Y, Z))

# def toDegrees(degreeValue):
#     """ converts radians to degrees """
#     return (degreeValue*57.2958)

def getBuildSpeed():
    """ calculates and returns build speed """
    scn, ag = getActiveContextInfo()
    return floor(ag.buildSpeed)

def getObjectVelocity():
    """ calculates and returns brick velocity """
    scn, ag = getActiveContextInfo()
    frameVelocity = round(2**(10-ag.velocity))
    return frameVelocity

def getAnimLength(objects_to_move, listZValues):
    scn, ag = getActiveContextInfo()
    tempObjCount = 0
    numLayers = 0
    while len(objects_to_move) > tempObjCount:
        numObjs = len(getNewSelection(listZValues))
        if numObjs != 0:
            numLayers += 1
            tempObjCount += numObjs
        elif not scn.skipEmptySelections:
            numLayers += 1
    return (numLayers - 1) * getBuildSpeed() + getObjectVelocity() + 1

def getPresetTuples(fileNames=None):
    # get list of filenames in presets directory
    if not fileNames:
        path = bpy.context.user_preferences.addons[bpy.props.assemblme_module_name].preferences.presetsFilepath
        fileNames = os.listdir(path)
    # refresh preset names
    fileNames.sort()
    presetNames = [(fileNames[i][:-3], fileNames[i][:-3], "Select this preset!") for i in range(len(fileNames)) if not fileNames[i].startswith(".") and fileNames[i].endswith(".py") and fileNames[i][:-3] not in ["__init__", "None"]]
    presetNames.append(("None", "None", "Don't use a preset"))
    return presetNames

# def setOrientation(orientation):
#     """ sets transform orientation """
#     if orientation == "custom":
#         bpy.ops.transform.create_orientation(name="LEGO Build Custom Orientation", use_view=False, use=True, overwrite=True)
#     else:
#         bpy.ops.transform.select_orientation(orientation=orientation)

def getListZValues(objects, rotXL=False, rotYL=False):
    """ returns list of dicts containing objects and ther z locations relative to layer orientation """
    scn, ag = getActiveContextInfo()

    # assemble list of dictionaries into 'listZValues'
    listZValues = []
    if not rotXL:
        rotXL = [getRandomizedOrient(ag.xOrient) for i in range(len(objects))]
        rotYL = [getRandomizedOrient(ag.yOrient) for i in range(len(objects))]
    for i,obj in enumerate(objects):
        l = obj.location
        rotX = rotXL[i]
        rotY = rotYL[i]
        zLoc = (l.z * cos(rotX) * cos(rotY)) + (l.x * sin(rotY)) + (l.y * -sin(rotX))
        listZValues.append({"loc":zLoc, "obj":obj})

    # sort list by "loc" key (relative z values)
    listZValues.sort(key=lambda x: x["loc"], reverse=not ag.invertBuild)

    # return list of dictionaries
    return listZValues, rotXL, rotYL

def getObjectsInBound(listZValues, z_lower_bound):
    """ select objects in bounds from listZValues """
    scn, ag = getActiveContextInfo()
    objsInBound = []
    # iterate through objects in listZValues (breaks when outside range)
    for i,lst in enumerate(listZValues):
        # set obj and z_loc
        obj = lst["obj"]
        z_loc = lst["loc"]
        # check if object is in bounding z value
        if z_loc >= z_lower_bound and not ag.invertBuild or z_loc <= z_lower_bound and ag.invertBuild:
            objsInBound.append(obj)
        # if not, break for loop and pop previous objects from listZValues
        else:
            for j in range(i):
                listZValues.pop(0)
            break
    return objsInBound

def getNewSelection(listZValues):
    """ selects next layer of objects """
    scn, ag = getActiveContextInfo()

    # get new upper and lower bounds
    props.z_upper_bound = listZValues[0]["loc"] if scn.skipEmptySelections or props.z_upper_bound is None else props.z_lower_bound
    props.z_lower_bound = props.z_upper_bound + ag.layerHeight * (1 if ag.invertBuild else -1)

    # select objects in bounds
    objsInBound = getObjectsInBound(listZValues, props.z_lower_bound)

    return objsInBound

def setBoundsForVisualizer(listZValues):
    for i in range(len(listZValues)):
        if listZValues[i]["obj"].type not in props.ignoredTypes:
            props.objMinLoc = listZValues[i]["obj"].location.copy()
            break
    for i in range(len(listZValues)-1,-1,-1):
        if listZValues[i]["obj"].type not in props.ignoredTypes:
            props.objMaxLoc = listZValues[i]["obj"].location.copy()
            break

def layers(l):
    all = [False]*20
    if type(l) == int:
        all[l] = True
    elif type(l) == list:
        for l in lList:
            allL[l] = True
    elif l.lower() == "all":
        all = [True]*20
    elif l.lower() == "none":
        pass
    elif l.lower() == "active":
        all = list(bpy.context.scene.layers)
    else:
        sys.stderr.write("Argument passed to 'layers()' function not recognized")
    return all

def updateAnimPreset(self, context):
    scn = bpy.context.scene
    if scn.animPreset != "None":
        import importlib.util
        pathToFile = os.path.join(bpy.context.user_preferences.addons[bpy.props.assemblme_module_name].preferences.presetsFilepath, scn.animPreset + ".py")
        if os.path.isfile(pathToFile):
            spec = importlib.util.spec_from_file_location(scn.animPreset + ".py", pathToFile)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            foo.execute()
        else:
            badPreset = str(scn.animPreset)
            if badPreset in scn.assemblme_default_presets:
                errorString = "Preset '%(badPreset)s' could not be found. This is a default preset – try reinstalling the addon to restore it." % locals()
            else:
                errorString = "Preset '%(badPreset)s' could not be found." % locals()
            sys.stderr.write(errorString)
            print(errorString)
            presetNames = getPresetTuples()

            bpy.types.Scene.animPreset = bpy.props.EnumProperty(
                name="Presets",
                description="Stored AssemblMe presets",
                items=presetNames,
                update=updateAnimPreset,
                default="None")

            bpy.types.Scene.animPresetToDelete = bpy.props.EnumProperty(
                name="Preset to Delete",
                description="Another list of stored AssemblMe presets",
                items=presetNames,
                default="None")
            scn.animPreset = "None"

    return None

def animateObjects(objects_to_move, listZValues, curFrame, locInterpolationMode='LINEAR', rotInterpolationMode='LINEAR'):
    """ animates objects """

    # initialize variables for use in while loop
    scn, ag = getActiveContextInfo()
    acc = 0
    lastUpdated = time.time()
    curTime = lastUpdated
    estTimeRemaining = []
    objects_moved = []
    last_len_objects_moved = 0
    mult = 1 if ag.buildType == "Assemble" else -1

    while len(objects_to_move) > len(objects_moved):
        # print status to terminal
        updateProgressBars(True, True, len(objects_moved) / len(objects_to_move), last_len_objects_moved / len(objects_to_move), "Animating Layers")
        last_len_objects_moved = len(objects_moved)

        # iterate num times in while loop
        acc += 1

        # get next objects to animate
        newSelection = getNewSelection(listZValues)

        # add objs to objects_moved
        objects_moved += newSelection

        # move selected objects and add keyframes
        kfIdxLoc = -1
        kfIdxRot = -1
        if len(newSelection) != 0:
            # insert location keyframes
            if ag.xLocOffset != 0 or ag.yLocOffset != 0 or ag.zLocOffset != 0 or ag.locationRandom != 0:
                insertKeyframes(newSelection, "location", curFrame, locInterpolationMode, kfIdxLoc)
                kfIdxLoc -= 1 if ag.buildType == "Assemble" else 0
            # insert rotation keyframes
            if ag.xRotOffset != 0 or ag.yRotOffset != 0 or ag.zRotOffset != 0 or ag.rotationRandom != 0:
                insertKeyframes(newSelection, "rotation_euler", curFrame, rotInterpolationMode, kfIdxRot)
                kfIdxLoc -= 1 if ag.buildType == "Assemble" else 0

            # set curFrame
            curFrame -= getObjectVelocity() * mult

            # move object and insert location keyframes
            if ag.xLocOffset != 0 or ag.yLocOffset != 0 or ag.zLocOffset != 0 or ag.locationRandom != 0:
                for obj in newSelection:
                    obj.location = getOffsetLocation(obj.location)
                insertKeyframes(newSelection, "location", curFrame, locInterpolationMode, kfIdxLoc)
            # rotate object and insert rotation keyframes
            if ag.xRotOffset != 0 or ag.yRotOffset != 0 or ag.zRotOffset != 0 or ag.rotationRandom != 0:
                for obj in newSelection:
                    obj.rotation_euler = getOffsetRotation(obj.rotation_euler)
                insertKeyframes(newSelection, "rotation_euler", curFrame, rotInterpolationMode, kfIdxRot)

            # set curFrame
            curFrame += getObjectVelocity() - getBuildSpeed() * mult

        # handle case where 'scn.skipEmptySelections' == False and empty selection is grabbed
        elif not scn.skipEmptySelections:
            # skip frame if nothing selected
            curFrame -= getBuildSpeed() * mult
        # handle case where 'scn.skipEmptySelections' == True and empty selection is grabbed
        else:
            os.stderr.write("Grabbed empty selection. This shouldn't happen!")

    updateProgressBars(True, True, 1, 0, "Animating Layers", end=True)

    return {"errorMsg":None, "moved":objects_moved, "lastFrame":curFrame}

def writeErrorToFile(errorReportPath, txtName, addonVersion):
    # write error to log text object
    if not os.path.exists(errorReportPath):
        os.makedirs(errorReportPath)
    fullFilePath = os.path.join(errorReportPath, "error_report.txt")
    f = open(fullFilePath, "w")
    f.write("\nPlease copy the following form and paste it into a new issue at https://github.com/bblanimation/assemblme/issues")
    f.write("\n\nDon't forget to include a description of your problem! The more information you provide (what you were trying to do, what action directly preceeded the error, etc.), the easier it will be for us to squash the bug.")
    f.write("\n\n### COPY EVERYTHING BELOW THIS LINE ###\n")
    f.write("\nDescription of the Problem:\n")
    f.write("\nBlender Version: " + bversion())
    f.write("\nAddon Version: " + addonVersion)
    f.write("\nPlatform Info:")
    f.write("\n   sysname = " + str(os.uname()[0]))
    f.write("\n   release = " + str(os.uname()[2]))
    f.write("\n   version = " + str(os.uname()[3]))
    f.write("\n   machine = " + str(os.uname()[4]))
    f.write("\nError:")
    try:
        f.write("\n" + bpy.data.texts[txtName].as_string())
    except:
        f.write(" No exception found")
