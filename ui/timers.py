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
from ..functions import *


def handle_selections():
    scn = bpy.context.scene
    obj = bpy.context.view_layer.objects.active
    # # if scn.layers changes and active object is no longer visible, set scn.aglist_index to -1
    # if scn.assemblMe_last_layers != str(list(scn.layers)):
    #     scn.assemblMe_last_layers = str(list(scn.layers))
    #     curCollVisible = False
    #     if scn.aglist_index != -1:
    #         ag0 = scn.aglist[scn.aglist_index]
    #         curCollVisible,_ = isCollectionVisible(scn, ag0)
    #     if not curCollVisible or scn.aglist_index == -1:
    #         setIndex = False
    #         for i,ag in enumerate(scn.aglist):
    #             if i != scn.aglist_index:
    #                 nextCollVisible,obj = isCollectionVisible(scn, ag)
    #                 if nextCollVisible and obj == obj:
    #                     scn.aglist_index = i
    #                     setIndex = True
    #                     break
    #         if not setIndex:
    #             scn.aglist_index = -1
    # select and make source or LEGO model active if scn.aglist_index changes
    if scn.assemblMe_last_aglist_index != scn.aglist_index and scn.aglist_index != -1:
        scn.assemblMe_last_aglist_index = scn.aglist_index
        ag = scn.aglist[scn.aglist_index]
        n = ag.collection_name
        coll = bpy.data.collections.get(n)
        if coll is not None and len(coll.objects) > 0:
            select(list(coll.objects), active=coll.objects[0])
            scn.assemblMe_last_active_object_name = obj.name
    # open LEGO model settings for active object if active object changes
    elif obj and scn.assemblMe_last_active_object_name != obj.name and (scn.aglist_index == -1 or scn.aglist[scn.aglist_index].collection_name != ""):# and obj.type == "MESH":
        scn.assemblMe_last_active_object_name = obj.name
        colls = []
        for c in obj.users_collection:
            colls.append(c.name)
        for i in range(len(scn.aglist)):
            ag = scn.aglist[i]
            if ag.collection_name in colls:
                scn.aglist_index = i
                scn.assemblMe_last_aglist_index = scn.aglist_index
                return 0.2
        scn.aglist_index = -1
    return 0.2
