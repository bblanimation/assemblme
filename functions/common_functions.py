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
props = bpy.props

def stopWatch(text, value):
    '''From seconds to Days;Hours:Minutes;Seconds'''

    valueD = (((value/365)/24)/60)
    Days = int(valueD)

    valueH = (valueD-Days)*365
    Hours = int(valueH)

    valueM = (valueH - Hours)*24
    Minutes = int(valueM)

    valueS = (valueM - Minutes)*60
    Seconds = int(valueS)

    # valueMs = (valueS - Seconds)*60
    # Miliseconds = int(valueMs)
    #
    print(str(text) + ": " + str(Days) + ";" + str(Hours) + ":" + str(Minutes) + ";" + str(Seconds)) # + ";;" + str(Miliseconds))

def groupExists(groupName):
    """ check if group exists in blender's memory """

    groupExists = False
    for group in bpy.data.groups:
        if group.name == groupName:
            groupExists = True
    return groupExists

# USE EXAMPLE: idfun=(lambda x: x.lower()) so that it ignores case
# https://www.peterbe.com/plog/uniqifiers-benchmark
def uniquify(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result
def uniquify1(seq):
   # Not order preserving
   keys = {}
   for e in seq:
       keys[e] = 1
   return keys.keys()

def confirmList(objList):
    """ if single object passed, convert to list """
    if type(objList) != list:
        objList = [objList]
    return objList

def insertKeyframes(objList, keyframeType, frame, interpolationMode='Default', idx=-1):
    """ insert key frames for given objects to given frames """
    objList = confirmList(objList)
    for obj in objList:
        obj.keyframe_insert(data_path=keyframeType, frame=frame)
        if interpolationMode != "Default":
            fcurves = []
            for i in range(3): # increase if inserting keyframes for something that takes up more than three fcurves
                fc = obj.animation_data.action.fcurves.find(keyframeType, index=i)
                if fc != None:
                    fcurves.append(fc)
            for fcurve in fcurves:
                # for kf in fcurve.keyframe_points:
                kf = fcurve.keyframe_points[idx]
                kf.interpolation = interpolationMode

def deselectAll():
    bpy.ops.object.select_all(action='DESELECT')
def selectAll():
    bpy.ops.object.select_all(action='SELECT')

def hide(objList):
    objList = confirmList(objList)
    for obj in objList:
        obj.hide = True
def unhide(objList):
    objList = confirmList(objList)
    for obj in objList:
        obj.hide = False

def select(objList=[], active=None, deselect=False, exclusive=True):
    """ selects objs in list and deselects the rest """
    objList = confirmList(objList)
    try:
        if not deselect:
            # deselect all if selection is exclusive
            if exclusive and len(objList) > 0:
                deselectAll()
            # select objects in list
            for obj in objList:
                obj.select = True
        elif deselect:
            # deselect objects in list
            for obj in objList:
                obj.select = False

        # set active object
        if active:
            try:
                bpy.context.scene.objects.active = active
            except:
                print("argument passed to 'active' parameter not valid (" + str(active) + ")")
    except:
        return False
    return True

def delete(objList):
    objList = confirmList(objList)
    objs = bpy.data.objects
    for obj in objList:
        objs.remove(obj, True)

def changeContext(context, areaType):
    """ Changes current context and returns previous area type """
    lastAreaType = context.area.type
    context.area.type = areaType
    return lastAreaType

def getLibraryPath():
    """ returns full path to module directory """
    functionsPath = os.path.dirname(os.path.abspath(__file__))
    libraryPath = functionsPath[:-10]
    if not os.path.exists(libraryPath):
        raise NameError("Did not find addon from path {}".format(libraryPath))
    return libraryPath

# https://github.com/CGCookie/retopoflow
def bversion():
    bversion = '%03d.%03d.%03d' % (bpy.app.version[0],bpy.app.version[1],bpy.app.version[2])
    return bversion

# https://github.com/CGCookie/retopoflow
def showErrorMessage(message, wrap=80):
    if not message: return
    lines = message.splitlines()
    if wrap > 0:
        nlines = []
        for line in lines:
            spc = len(line) - len(line.lstrip())
            while len(line) > wrap:
                i = line.rfind(' ',0,wrap)
                if i == -1:
                    nlines += [line[:wrap]]
                    line = line[wrap:]
                else:
                    nlines += [line[:i]]
                    line = line[i+1:]
                if line:
                    line = ' '*spc + line
            nlines += [line]
        lines = nlines
    def draw(self,context):
        for line in lines:
            self.layout.label(line)
    bpy.context.window_manager.popup_menu(draw, title="Error Message", icon="ERROR")
    return

# http://stackoverflow.com/questions/14519177/python-exception-handling-line-number
def print_exception(txtName, showError=False):
    exc_type, exc_obj, tb = sys.exc_info()

    errormsg = 'EXCEPTION (%s): %s\n' % (exc_type, exc_obj)
    etb = traceback.extract_tb(tb)
    pfilename = None
    for i,entry in enumerate(reversed(etb)):
        filename,lineno,funcname,line = entry
        if filename != pfilename:
            pfilename = filename
            errormsg += '         %s\n' % (filename)
        errormsg += '%03d %04d:%s() %s\n' % (i, lineno, funcname, line.strip())

    print(errormsg)

    if txtName not in bpy.data.texts:
        # create a log file for error writing
        bpy.ops.text.new()
        bpy.data.texts[-1].name = txtName

    # write error to log text object
    bpy.data.texts[txtName].write(errormsg + '\n')

    if showError:
        showErrorMessage(errormsg, wrap=240)

    return errormsg
