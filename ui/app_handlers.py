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
import math
from bpy.app.handlers import persistent
from ..functions import *
from mathutils import Vector, Euler

def isCollectionVisible(scn, ag):
    return False, None
    # TODO: rewrite to check if collection is visible
    scn = bpy.context.scene
    n = ag.collection_name
    objectsOnActiveLayers = []
    objects = scn.objects
    for i in range(20):
        # get objects on current layer if layer is active for object and scene
        objectsOnActiveLayers += [ob for ob in objects if ob.layers[i] and scn.layers[i]]
    for obj in objectsOnActiveLayers:
        if bpy.data.collections.get(n) in obj.users_collection:
            return True, obj
    return False, None

@persistent
def handle_selections(scene):
    scn = bpy.context.scene
    try:
        assemblMeIsActive = bpy.props.assemblme_module_name in bpy.context.user_preferences.addons.keys()
    except:
        assemblMeIsActive = False
    if assemblMeIsActive:
        # if scn.layers changes and active object is no longer visible, set scn.aglist_index to -1
        if scn.assemblMe_last_layers != str(list(scn.layers)):
            scn.assemblMe_last_layers = str(list(scn.layers))
            curCollVisible = False
            if scn.aglist_index != -1:
                ag0 = scn.aglist[scn.aglist_index]
                curCollVisible,_ = isCollectionVisible(scn, ag0)
            if not curCollVisible or scn.aglist_index == -1:
                setIndex = False
                for i,ag in enumerate(scn.aglist):
                    if i != scn.aglist_index:
                        nextCollVisible,obj = isCollectionVisible(scn, ag)
                        if nextCollVisible and bpy.context.active_object == obj:
                            scn.aglist_index = i
                            setIndex = True
                            break
                if not setIndex:
                    scn.aglist_index = -1
        # select and make source or LEGO model active if scn.aglist_index changes
        elif scn.assemblMe_last_aglist_index != scn.aglist_index and scn.aglist_index != -1:
            scn.assemblMe_last_aglist_index = scn.aglist_index
            ag = scn.aglist[scn.aglist_index]
            n = ag.collection_name
            coll = bpy.data.collections.get(n)
            if coll is not None and len(coll.objects) > 0:
                select(list(coll.objects), active=coll.objects[0])
                scn.assemblMe_last_active_object_name = bpy.context.object.name
        # open LEGO model settings for active object if active object changes
    elif bpy.context.object and scn.assemblMe_last_active_object_name != bpy.context.object.name and ( scn.aglist_index == -1 or scn.aglist[scn.aglist_index].collection_name != ""):# and bpy.context.object.type == "MESH":
            scn.assemblMe_last_active_object_name = bpy.context.object.name
            colls = []
            for c in bpy.context.object.users_collection:
                colls.append(c.name)
            for i in range(len(scn.aglist)):
                ag = scn.aglist[i]
                if ag.collection_name in colls:
                    scn.aglist_index = i
                    scn.assemblMe_last_aglist_index = scn.aglist_index
                    return
            scn.aglist_index = -1

# bpy.app.handlers.scene_update_pre.append(handle_selections)


@persistent
def convert_velocity_value(scene):
    scn = bpy.context.scene
    try:
        assemblMeIsActive = bpy.props.assemblme_module_name in bpy.context.user_preferences.addons.keys()
    except:
        assemblMeIsActive = False
    if assemblMeIsActive:
        for ag in scn.aglist:
            if ag.objectVelocity != -1:
                oldV = ag.objectVelocity
                targetNumFrames = 51 - oldV
                ag.velocity = 10 - (math.log(targetNumFrames, 2))
                ag.objectVelocity = -1

bpy.app.handlers.load_post.append(convert_velocity_value)


@persistent
def handle_upconversion(scene):
    scn = bpy.context.scene
    # update storage scene name
    for ag in scn.aglist:
        if createdWithUnsupportedVersion(ag):
            # convert from v1_1 to v1_2
            if int(ag.version[2]) < 2:
                if ag.group_name.startswith("AssemblMe_animated_group"):
                    curGroup = bpy.data.groups.get(ag.group_name)
                    curGroup.name = "AssemblMe_{}_group".format(ag.name)
                    ag.group_name = curGroup.name

bpy.app.handlers.load_post.append(handle_upconversion)
