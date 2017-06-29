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
from .mesh_generate import *
props = bpy.props

def getRandomizedOrient(orient):
    """ returns randomized orientation based on user settings """
    scn = bpy.context.scene
    return (orient + random.uniform(-scn.orientRandom, scn.orientRandom))

def getOffsetLocation(location):
    """ returns randomized location offset """
    scn = bpy.context.scene
    X = location.x + random.uniform(-scn.locationRandom, scn.locationRandom) + scn.xLocOffset
    Y = location.y + random.uniform(-scn.locationRandom, scn.locationRandom) + scn.yLocOffset
    Z = location.z + random.uniform(-scn.locationRandom, scn.locationRandom) + scn.zLocOffset
    return (X, Y, Z)

def getOffsetRotation(rotation):
    """ returns randomized rotation offset """
    scn = bpy.context.scene
    X = rotation.x + random.uniform(-scn.rotationRandom, scn.rotationRandom) + scn.xRotOffset
    Y = rotation.y + random.uniform(-scn.rotationRandom, scn.rotationRandom) + scn.yRotOffset
    Z = rotation.z + random.uniform(-scn.rotationRandom, scn.rotationRandom) + scn.zRotOffset
    return {"X":X, "Y":Y, "Z":Z}

# def toDegrees(degreeValue):
#     """ converts radians to degrees """
#     return (degreeValue*57.2958)

def getBuildSpeed():
    """ calculates and returns build speed """
    return floor(bpy.context.scene.buildSpeed)

def getObjectVelocity():
    """ calculates and returns brick velocity """
    return floor(51-(bpy.context.scene.objectVelocity))

def getAnimLength():
    scn = bpy.context.scene
    tempObjCount = 0
    numLayers = 0
    while len(props.objects_to_move) > tempObjCount:
        numObjs = len(getNewSelection())
        if numObjs != 0:
            numLayers += 1
            tempObjCount += numObjs
        elif not scn.skipEmptySelections:
            numLayers += 1
    return (numLayers - 1) * getBuildSpeed() + getObjectVelocity() + 1

# def setOrientation(orientation):
#     """ sets transform orientation """
#     if orientation == "custom":
#         bpy.ops.transform.create_orientation(name="LEGO Build Custom Orientation", use_view=False, use=True, overwrite=True)
#     else:
#         bpy.ops.transform.select_orientation(orientation=orientation)

def getListZValues(objects):
    """ returns list of dicts containing objects and ther z locations relative to layer orientation """
    scn = bpy.context.scene

    # assemble list of dictionaries into 'listZValues'
    listZValues = []
    for obj in objects:
        l = obj.location
        rotX = getRandomizedOrient(scn.xOrient)
        rotY = getRandomizedOrient(scn.yOrient)
        zLoc = (l.z * cos(rotX) * cos(rotY)) + (l.x * sin(rotY)) + (l.y * -sin(rotX))
        listZValues.append({"loc":zLoc, "obj":obj})

    # sort list by "loc" key (relative z values)
    if scn.invertBuild:
        listZValues.sort(key=lambda x: x["loc"])
    else:
        listZValues.sort(key=lambda x: x["loc"], reverse=True)

    # return list of dictionaries
    return listZValues

def getObjectsInBound():
    """ select objects in bounds from props.listZValues """
    scn = bpy.context.scene
    objsInBound = []
    # iterate through objects in listZValues (breaks when outside range)
    for i,lst in enumerate(props.listZValues):
        # set obj and z_loc
        obj = lst["obj"]
        z_loc = lst["loc"]
        # if object is camera or lamp, remove from props.objects_to_move
        if obj.type in props.ignoredTypes:
            props.objects_to_move.remove(obj)
            continue
        # check if object is in bounding z value
        if z_loc >= props.z_lower_bound and not scn.invertBuild or z_loc <= props.z_lower_bound and scn.invertBuild:
            objsInBound.append(obj)
        # if not, break for loop and pop previous objects from listZValues
        else:
            for j in range(i):
                props.listZValues.pop(0)
            break
    return objsInBound

def getNewSelection():
    """ selects next layer of objects """

    scn = bpy.context.scene

    # get new upper and lower bounds
    if scn.skipEmptySelections or props.z_upper_bound == None:
        props.z_upper_bound = props.listZValues[0]["loc"]
    else:
        props.z_upper_bound = props.z_lower_bound
    if scn.invertBuild:
        props.z_lower_bound = props.z_upper_bound + scn.layerHeight
    else:
        props.z_lower_bound = props.z_upper_bound - scn.layerHeight

    # select objects in bounds
    objsInBound = getObjectsInBound()

    return objsInBound

def setBoundsForVisualizer():
    for i in range(len(props.listZValues)):
        if props.listZValues[i]["obj"].type not in props.ignoredTypes:
            props.objMinLoc = props.listZValues[i]["obj"].location.copy()
            break
    for i in range(len(props.listZValues)-1,-1,-1):
        if props.listZValues[i]["obj"].type not in props.ignoredTypes:
            props.objMaxLoc = props.listZValues[i]["obj"].location.copy()
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

def updateAnimType(self, context):
    scn = bpy.context.scene
    if scn.animType == "Custom":
        pass
    elif scn.animType == "Standard Build":
        from ..buttons.visualizer import visualizer
        scn.buildSpeed = 1
        scn.objectVelocity = 30
        scn.xLocOffset = 0
        scn.yLocOffset = 0
        scn.zLocOffset = 20
        scn.locInterpolationMode = "CUBIC"
        scn.locationRandom = 0
        scn.xRotOffset = 0
        scn.yRotOffset = 0
        scn.zRotOffset = 0
        scn.rotInterpolationMode = "LINEAR"
        scn.rotationRandom = 0
        scn.xOrient = 0
        scn.yOrient = 0
        scn.orientRandom = 0.001
        scn.layerHeight = 0.01
        scn.buildType = "Assemble"
        scn.invertBuild = False
        if groupExists("AssemblMe_visualizer"):
            visualizer.disable(visualizer, bpy.context)
    elif scn.animType == "Explode":
        scn.buildSpeed = 1
        scn.objectVelocity = 15
        scn.xLocOffset = 0
        scn.yLocOffset = 0
        scn.zLocOffset = 0
        scn.locInterpolationMode = "LINEAR"
        scn.locationRandom = 50
        scn.xRotOffset = 0
        scn.yRotOffset = 0
        scn.zRotOffset = 0
        scn.rotInterpolationMode = "LINEAR"
        scn.rotationRandom = 20
        scn.xOrient = 0
        scn.yOrient = 0
        scn.orientRandom = 50
        scn.layerHeight = 15
        scn.buildType = "Disassemble"
        scn.invertBuild = False
        if groupExists("AssemblMe_visualizer"):
            visualizer.disable(visualizer, bpy.context)

    return None

def animateObjects(objectsToMove, curFrame, locInterpolationMode='LINEAR', rotInterpolationMode='LINEAR'):
    """ animates objects """

    # initialize variables for use in while loop
    scn = bpy.context.scene
    acc = 0
    lastUpdated = time.time()
    curTime = lastUpdated
    estTimeRemaining = []
    objects_moved = []
    axisObj = bpy.data.groups['AssemblMe_axis_obj'].objects[0]


    while len(objectsToMove) > 0:
        # iterate num times in while loop
        acc += 1

        # deselect all
        bpy.ops.object.select_all(action='DESELECT')

        # select next objects to animate
        newSelection = getNewSelection()
        select(newSelection)

        # print time remaining
        if scn.printStatus:
            # update timekeeper variables
            lastTime = curTime
            curTime = time.time()
            # ignore first value
            if acc > 1:
                # calculate remaining frames
                if scn.buildType == "Assemble":
                    framesRemaining = curFrame - scn.firstFrame - getObjectVelocity() - getBuildSpeed()
                else:
                    framesRemaining = scn.animLength - curFrame - getObjectVelocity()
                # calculate and print time remaining
                timeElapsed = curTime-lastTime
                estTimeRemaining.append(timeElapsed * framesRemaining)
                if curTime - lastUpdated >= scn.updateFrequency:
                    stopWatch("Time Remaining", sum(estTimeRemaining)/len(estTimeRemaining))
                    estTimeRemaining = []
                    lastUpdated = curTime

        # iterate through selected objects
        for obj in bpy.context.selected_objects:
            # set object parent to axisObj
            obj.parent = axisObj
            # put selected objects in 'objects_moved'
            objects_moved.append(obj)
            # obj no longer needs to be moved, so remove from 'objects_to_move'
            objectsToMove.remove(obj)

        # move selected objects and add keyframes
        if len(bpy.context.selected_objects) != 0:
            # insert location keyframes
            if scn.xLocOffset != 0 or scn.yLocOffset != 0 or scn.zLocOffset != 0 or scn.locationRandom != 0:
                insertKeyframes(bpy.context.selected_objects, "location", curFrame, locInterpolationMode)
            # insert rotation keyframes
            if scn.xRotOffset != 0 or scn.yRotOffset != 0 or scn.zRotOffset != 0 or scn.rotationRandom != 0:
                insertKeyframes(bpy.context.selected_objects, "rotation_euler", curFrame, rotInterpolationMode)

            # set curFrame
            if scn.buildType == "Assemble":
                curFrame -= getObjectVelocity()
            else:
                curFrame += getObjectVelocity()

            # move object and insert location keyframes
            if scn.xLocOffset != 0 or scn.yLocOffset != 0 or scn.zLocOffset != 0 or scn.locationRandom != 0:
                for obj in bpy.context.selected_objects:
                    obj.location = getOffsetLocation(obj.location)
                insertKeyframes(bpy.context.selected_objects, "location", curFrame, locInterpolationMode)
            # rotate object and insert rotation keyframes
            if scn.xRotOffset != 0 or scn.yRotOffset != 0 or scn.zRotOffset != 0 or scn.rotationRandom != 0:
                for obj in bpy.context.selected_objects:
                    offsetRotation = getOffsetRotation(obj.rotation_euler)
                    obj.rotation_euler.x = offsetRotation["X"]
                    obj.rotation_euler.y = offsetRotation["Y"]
                    obj.rotation_euler.z = offsetRotation["Z"]
                insertKeyframes(bpy.context.selected_objects, "rotation_euler", curFrame, rotInterpolationMode)

            # set curFrame
            if scn.buildType == "Assemble":
                curFrame += getObjectVelocity() - getBuildSpeed()
            else:
                curFrame += getBuildSpeed() - getObjectVelocity()


        # handle case where 'scn.skipEmptySelections' == False and empty selection is grabbed
        elif not scn.skipEmptySelections:
            # skip frame if nothing selected
            if scn.buildType == "Assemble":
                curFrame -= getBuildSpeed()
            else:
                curFrame += getBuildSpeed()
        # handle case where 'scn.skipEmptySelections' == True and empty selection is grabbed
        else:
            self.report({"ERROR"}, "Grabbed empty selection. This shouldn't happen!")

    return {"errorMsg":None, "moved":objects_moved, "lastFrame":curFrame}
