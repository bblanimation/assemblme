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
from bpy.app.handlers import persistent
from ..functions import *
from mathutils import Vector, Euler

def isGroupVisible(scn, ag):
    scn = bpy.context.scene
    n = ag.group_name
    objectsOnActiveLayers = []
    objects = scn.objects
    for i in range(20):
        # get objects on current layer if layer is active for object and scene
        objectsOnActiveLayers += [ob for ob in objects if ob.layers[i] and scn.layers[i]]
    for obj in objectsOnActiveLayers:
        if bpy.data.groups.get(n) in obj.users_group:
            return True, obj
    return False, None

@persistent
def handle_selections(scene):
    scn = bpy.context.scene
    if 'assemblme' in bpy.context.user_preferences.addons.keys():
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
            n = ag.group_name
            group = bpy.data.groups.get(n)
            if group is not None and len(group.objects) > 0:
                select(list(group.objects), active=group.objects[0])
                scn.assemblMe_last_active_object_name = scn.objects.active.name
        # open LEGO model settings for active object if active object changes
        elif scn.objects.active and scn.assemblMe_last_active_object_name != scn.objects.active.name and ( scn.aglist_index == -1 or scn.aglist[scn.aglist_index].group_name != ""):# and scn.objects.active.type == "MESH":
            scn.assemblMe_last_active_object_name = scn.objects.active.name
            groups = []
            for g in scn.objects.active.users_group:
                groups.append(g.name)
            for i in range(len(scn.aglist)):
                ag = scn.aglist[i]
                if ag.group_name in groups:
                    scn.aglist_index = i
                    scn.assemblMe_last_aglist_index = scn.aglist_index
                    return
            scn.aglist_index = -1

bpy.app.handlers.scene_update_pre.append(handle_selections)
