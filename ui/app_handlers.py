# Copyright (C) 2018 Christopher Gearhart
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

# system imports
import bpy
import math
from bpy.app.handlers import persistent
from ..functions import *
from mathutils import Vector, Euler

def isGroupVisible(scn, ag):
    scn = bpy.context.scene
    objectsOnActiveLayers = []
    objects = scn.objects
    for i in range(20):
        # get objects on current layer if layer is active for object and scene
        objectsOnActiveLayers += [ob for ob in objects if ob.layers[i] and scn.layers[i]]
    for obj in objectsOnActiveLayers:
        if ag.group in obj.users_group:
            return True, obj
    return False, None

@persistent
def handle_selections(scn):
    # if scn.layers changes and active object is no longer visible, set scn.aglist_index to -1
    if scn.assemblMe_last_layers != str(list(scn.layers)):
        scn.assemblMe_last_layers = str(list(scn.layers))
        curGroupVisible = False
        if scn.aglist_index != -1:
            ag0 = scn.aglist[scn.aglist_index]
            curGroupVisible,_ = isGroupVisible(scn, ag0)
        if not curGroupVisible or scn.aglist_index == -1:
            setIndex = False
            for i,ag in enumerate(scn.aglist):
                if i != scn.aglist_index:
                    nextGroupVisible,obj = isGroupVisible(scn, ag)
                    if nextGroupVisible and bpy.context.active_object == obj:
                        scn.aglist_index = i
                        setIndex = True
                        break
            if not setIndex:
                scn.aglist_index = -1
    # select and make source or LEGO model active if scn.aglist_index changes
    elif scn.assemblMe_last_aglist_index != scn.aglist_index and scn.aglist_index != -1:
        scn.assemblMe_last_aglist_index = scn.aglist_index
        ag = scn.aglist[scn.aglist_index]
        group = ag.group
        if group is not None and len(group.objects) > 0:
            select(list(group.objects), active=group.objects[0])
            scn.assemblMe_last_active_object_name = bpy.context.active_object.name
    # open LEGO model settings for active object if active object changes
    elif bpy.context.active_object and scn.assemblMe_last_active_object_name != bpy.context.active_object.name and (scn.aglist_index == -1 or scn.aglist[scn.aglist_index].group is not None):# and bpy.context.active_object.type == "MESH":
        scn.assemblMe_last_active_object_name = bpy.context.active_object.name
        groups = []
        for g in bpy.context.active_object.users_group:
            groups.append(g)
        for i in range(len(scn.aglist)):
            ag = scn.aglist[i]
            if ag.group in groups:
                scn.aglist_index = i
                scn.assemblMe_last_aglist_index = scn.aglist_index
                return
        scn.aglist_index = -1

@persistent
def convert_velocity_value(scn):
    if scn is None:
        return
    for ag in scn.aglist:
        if ag.objectVelocity != -1:
            oldV = ag.objectVelocity
            targetNumFrames = 51 - oldV
            ag.velocity = 10 - (math.log(targetNumFrames, 2))
            ag.objectVelocity = -1


@persistent
def handle_upconversion(scn):
    if scn is None:
        return
    # update storage scene name
    for ag in scn.aglist:
        if createdWithUnsupportedVersion(ag):
            # convert from v1_1 to v1_2
            if int(ag.version[2]) < 2:
                if ag.group and ag.group.name.startswith("AssemblMe_animated_group"):
                    ag.group.name = "AssemblMe_{}_group".format(ag.name)
