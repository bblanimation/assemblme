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
import random
import sys
import time
import os
import traceback
from math import *
from .common_functions import *
from .common_mesh_generate import *
props = bpy.props

def getRandomizedOrient(orient):
    """ returns randomized orientation based on user settings """
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    return (orient + random.uniform(-ag.orientRandom, ag.orientRandom))

def getOffsetLocation(location):
    """ returns randomized location offset """
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    X = location.x + random.uniform(-ag.locationRandom, ag.locationRandom) + ag.xLocOffset
    Y = location.y + random.uniform(-ag.locationRandom, ag.locationRandom) + ag.yLocOffset
    Z = location.z + random.uniform(-ag.locationRandom, ag.locationRandom) + ag.zLocOffset
    return (X, Y, Z)

def getOffsetRotation(rotation):
    """ returns randomized rotation offset """
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    X = rotation.x + random.uniform(-ag.rotationRandom, ag.rotationRandom) + ag.xRotOffset
    Y = rotation.y + random.uniform(-ag.rotationRandom, ag.rotationRandom) + ag.yRotOffset
    Z = rotation.z + random.uniform(-ag.rotationRandom, ag.rotationRandom) + ag.zRotOffset
    return {"X":X, "Y":Y, "Z":Z}

# def toDegrees(degreeValue):
#     """ converts radians to degrees """
#     return (degreeValue*57.2958)

def getBuildSpeed():
    """ calculates and returns build speed """
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    return floor(ag.buildSpeed)

def getObjectVelocity():
    """ calculates and returns brick velocity """
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    frameVelocity = floor(2**(10-ag.velocity))
    return frameVelocity

def getAnimLength(objectsToMove, listZValues):
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    tempObjCount = 0
    numLayers = 0
    while len(objectsToMove) > tempObjCount:
        numObjs = len(getNewSelection(objectsToMove, listZValues))
        if numObjs != 0:
            numLayers += 1
            tempObjCount += numObjs
        elif not scn.skipEmptySelections:
            numLayers += 1
    return (numLayers - 1) * getBuildSpeed() + getObjectVelocity() + 1

def getPresetTuples(fileNames=None):
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

# def setOrientation(orientation):
#     """ sets transform orientation """
#     if orientation == "custom":
#         bpy.ops.transform.create_orientation(name="LEGO Build Custom Orientation", use_view=False, use=True, overwrite=True)
#     else:
#         bpy.ops.transform.select_orientation(orientation=orientation)

def getListZValues(objects, rotXL=False, rotYL=False):
    """ returns list of dicts containing objects and ther z locations relative to layer orientation """
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]

    # assemble list of dictionaries into 'listZValues'
    listZValues = []
    if not rotXL:
        rotXL = []
        rotYL = []
        for i in range(len(objects)):
            rotXL.append(getRandomizedOrient(ag.xOrient))
            rotYL.append(getRandomizedOrient(ag.yOrient))
    for i,obj in enumerate(objects):
        l = obj.location
        rotX = rotXL[i]
        rotY = rotYL[i]
        zLoc = (l.z * cos(rotX) * cos(rotY)) + (l.x * sin(rotY)) + (l.y * -sin(rotX))
        listZValues.append({"loc":zLoc, "obj":obj})

    # sort list by "loc" key (relative z values)
    if ag.invertBuild:
        listZValues.sort(key=lambda x: x["loc"])
    else:
        listZValues.sort(key=lambda x: x["loc"], reverse=True)

    # return list of dictionaries
    return listZValues,rotXL,rotYL

def getObjectsInBound(objectsToMove, listZValues, z_lower_bound):
    """ select objects in bounds from listZValues """
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    objsInBound = []
    # iterate through objects in listZValues (breaks when outside range)
    for i,lst in enumerate(listZValues):
        # set obj and z_loc
        obj = lst["obj"]
        z_loc = lst["loc"]
        # if object is camera or lamp, remove from objectsToMove
        if obj.type in props.ignoredTypes:
            objectsToMove.remove(obj)
            continue
        # check if object is in bounding z value
        if z_loc >= z_lower_bound and not ag.invertBuild or z_loc <= z_lower_bound and ag.invertBuild:
            objsInBound.append(obj)
        # if not, break for loop and pop previous objects from listZValues
        else:
            for j in range(i):
                listZValues.pop(0)
            break
    return objsInBound

def getNewSelection(objectsToMove, listZValues):
    """ selects next layer of objects """
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]

    # get new upper and lower bounds
    if scn.skipEmptySelections or props.z_upper_bound == None:
        props.z_upper_bound = listZValues[0]["loc"]
    else:
        props.z_upper_bound = props.z_lower_bound
    if ag.invertBuild:
        props.z_lower_bound = props.z_upper_bound + ag.layerHeight
    else:
        props.z_lower_bound = props.z_upper_bound - ag.layerHeight

    # select objects in bounds
    objsInBound = getObjectsInBound(objectsToMove, listZValues, props.z_lower_bound)

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

def setOrigin(objList, originToType):
    objList = confirmList(objList)
    select(objList)
    bpy.ops.object.origin_set(type=originToType)

def updateAnimPreset(self, context):
    scn = bpy.context.scene
    if scn.animPreset != "None":
        import importlib.util
        pathToFile = os.path.join(props.addon_prefs.presetsFilepath, scn.animPreset + ".py")
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

    if groupExists("AssemblMe_visualizer"):
        if scn.animPreset == "Standard Build" or scn.animPreset == "Explode":
            visualizer.disable(visualizer, bpy.context)

    scn.animPresetToDelete = scn.animPreset

    return None

def animateObjects(objectsToMove, listZValues, curFrame, locInterpolationMode='LINEAR', rotInterpolationMode='LINEAR'):
    """ animates objects """

    # initialize variables for use in while loop
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    acc = 0
    lastUpdated = time.time()
    curTime = lastUpdated
    estTimeRemaining = []
    objects_moved = []
    # axisObj = bpy.data.groups['AssemblMe_axis_obj'].objects[0]

    while len(objectsToMove) > 0:
        # iterate num times in while loop
        acc += 1

        # get next objects to animate
        newSelection = getNewSelection(objectsToMove, listZValues)

        # iterate through selected objects
        for obj in newSelection:
            # # set object parent to axisObj
            # obj.parent = axisObj
            # put selected objects in 'objects_moved'
            objects_moved.append(obj)
            # obj no longer needs to be moved, so remove from 'objectsToMove'
            objectsToMove.remove(obj)

        # move selected objects and add keyframes
        kfIdxLoc = -1
        kfIdxRot = -1
        if len(newSelection) != 0:
            # insert location keyframes
            if ag.xLocOffset != 0 or ag.yLocOffset != 0 or ag.zLocOffset != 0 or ag.locationRandom != 0:
                insertKeyframes(newSelection, "location", curFrame, locInterpolationMode, kfIdxLoc)
                if ag.buildType == "Assemble":
                    kfIdxLoc -= 1
            # insert rotation keyframes
            if ag.xRotOffset != 0 or ag.yRotOffset != 0 or ag.zRotOffset != 0 or ag.rotationRandom != 0:
                insertKeyframes(newSelection, "rotation_euler", curFrame, rotInterpolationMode, kfIdxRot)
                if ag.buildType == "Assemble":
                    kfIdxRot -= 1

            # set curFrame
            if ag.buildType == "Assemble":
                curFrame -= getObjectVelocity()
            else:
                curFrame += getObjectVelocity()

            # move object and insert location keyframes
            if ag.xLocOffset != 0 or ag.yLocOffset != 0 or ag.zLocOffset != 0 or ag.locationRandom != 0:
                for obj in newSelection:
                    obj.location = getOffsetLocation(obj.location)
                insertKeyframes(newSelection, "location", curFrame, locInterpolationMode, kfIdxLoc)
            # rotate object and insert rotation keyframes
            if ag.xRotOffset != 0 or ag.yRotOffset != 0 or ag.zRotOffset != 0 or ag.rotationRandom != 0:
                for obj in newSelection:
                    offsetRotation = getOffsetRotation(obj.rotation_euler)
                    obj.rotation_euler.x = offsetRotation["X"]
                    obj.rotation_euler.y = offsetRotation["Y"]
                    obj.rotation_euler.z = offsetRotation["Z"]
                insertKeyframes(newSelection, "rotation_euler", curFrame, rotInterpolationMode, kfIdxRot)

            # set curFrame
            if ag.buildType == "Assemble":
                curFrame += getObjectVelocity() - getBuildSpeed()
            else:
                curFrame += getBuildSpeed() - getObjectVelocity()


        # handle case where 'scn.skipEmptySelections' == False and empty selection is grabbed
        elif not scn.skipEmptySelections:
            # skip frame if nothing selected
            if ag.buildType == "Assemble":
                curFrame -= getBuildSpeed()
            else:
                curFrame += getBuildSpeed()
        # handle case where 'scn.skipEmptySelections' == True and empty selection is grabbed
        else:
            os.stderr.write("Grabbed empty selection. This shouldn't happen!")

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
