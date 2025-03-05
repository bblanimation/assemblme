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
# NONE!

# Blender imports
import bpy
from bpy.app.handlers import persistent

# Module imports
from ..functions import *


@persistent
def handle_selections(junk=None):
    scn = bpy.context.scene
    obj = bpy.context.view_layer.objects.active
    # open LEGO model settings for active object if active object changes
    if obj and scn.assemblme.last_active_object_name != obj.name and (scn.aglist_index == -1 or scn.aglist[scn.aglist_index].collection is not None):# and obj.type == "MESH":
        scn.assemblme.last_active_object_name = obj.name
        # do nothing, because the active aglist index refers to this collection
        if scn.aglist_index != -1 and scn.aglist[scn.aglist_index].collection in (obj.users_collection):
            return 0.2
        # attempt to switch aglist index if one of them refers to this collection
        for i in range(len(scn.aglist)):
            ag = scn.aglist[i]
            if ag.collection in (obj.users_collection):
                scn.aglist_index = i
                tag_redraw_areas("VIEW_3D")
                return 0.2
        scn.aglist_index = -1
    return 0.2


@persistent
@blender_version_wrapper('>=','2.80')
def register_assemblme_timers(scn, junk=None):
    timer_fns = (handle_selections,)
    for timer_fn in timer_fns:
        if not bpy.app.timers.is_registered(timer_fn):
            bpy.app.timers.register(timer_fn)
