bl_info = {
    "name"        : "AssemblMe",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 2, 0),
    "blender"     : (2, 79, 0),
    "description" : "Iterative object assembly animations made simple",
    "location"    : "View3D > Tools > AssemblMe",
    "wiki_url"    : "https://www.blendermarket.com/products/assemblme",
    "tracker_url" : "https://github.com/bblanimation/assemblme/issues",
    "category"    : "Animation"}

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
import os
from bpy.props import *
from .ui import *
from .buttons import *
from .functions import getPresetTuples

# updater import
from . import addon_updater_ops
from .buttons.presets import *
from .lib.preferences import *


def register():
    bpy.utils.register_module(__name__)

    bpy.props.assemblme_module_name = __name__
    bpy.props.assemblme_module_path = os.path.dirname(os.path.abspath(__file__))
    bpy.props.assemblme_version = str(bl_info["version"])[1:-1]
    bpy.props.assemblme_preferences = bpy.context.user_preferences.addons[__package__].preferences

    bpy.types.Scene.assemblme_copy_from_id = IntProperty(default=-1)

    # items used by selection app handler
    bpy.types.Scene.assemblMe_runningOperation = BoolProperty(default=False)
    bpy.types.Scene.assemblMe_last_layers = StringProperty(default="")
    bpy.types.Scene.assemblMe_last_aglist_index = IntProperty(default=-2)
    bpy.types.Scene.assemblMe_active_object_name = StringProperty(default="")
    bpy.types.Scene.assemblMe_last_active_object_name = StringProperty(default="")

    bpy.types.Scene.skipEmptySelections = BoolProperty(
        name="Skip Empty Selections",
        description="Skip frames where nothing is selected if checked (Recommended)",
        default=True)

    bpy.types.Scene.newPresetName = StringProperty(
        name="Name of New Preset",
        description="Full name of new custom preset",
        default="")
    bpy.types.Scene.assemblme_default_presets = ["Explode", "Rain", "Standard Build", "Step-by-Step"]
    presetNames = getPresetTuples(transferDefaults=True)
    bpy.types.Scene.animPreset = EnumProperty(
        name="Presets",
        description="Stored AssemblMe presets",
        items=presetNames,
        update=updateAnimPreset,
        default="None")
    bpy.types.Scene.animPresetToDelete = EnumProperty(
        name="Preset to Delete",
        description="Another list of stored AssemblMe presets",
        items=bpy.types.Scene.animPreset[1]['items'],
        default="None")

    bpy.types.Scene.visualizerScale = FloatProperty(
        name="Scale",
        description="Scale of layer orientation visualizer",
        precision=1,
        min=0.1, max=16,
        default=10)
    bpy.types.Scene.visualizerRes = FloatProperty(
        name="Resolution",
        description="Resolution of layer orientation visualizer",
        precision=2,
        min=0.05, max=1,
        default=0.25)

    # list properties
    bpy.types.Scene.aglist = CollectionProperty(type=AssemblMe_AnimatedGroups)
    bpy.types.Scene.aglist_index = IntProperty(default=-1)

    # Session properties
    bpy.props.z_upper_bound = None
    bpy.props.z_lower_bound = None
    bpy.props.objMinLoc = 0
    bpy.props.objMaxLoc = 0

    # addon updater code and configurations
    addon_updater_ops.register(bl_info)


def unregister():
    Scn = bpy.types.Scene

    # addon updater unregister
    addon_updater_ops.unregister()

    del bpy.props.z_upper_bound
    del bpy.props.z_lower_bound
    del bpy.props.objMinLoc
    del bpy.props.objMaxLoc

    del Scn.aglist_index
    del Scn.aglist

    del Scn.visualizerRes
    del Scn.visualizerScale

    del Scn.animPresetToDelete
    del Scn.animPreset
    del Scn.newPresetName

    del Scn.skipEmptySelections

    del Scn.assemblMe_last_active_object_name
    del Scn.assemblMe_active_object_name
    del Scn.assemblMe_last_aglist_index
    del Scn.assemblMe_last_layers
    del Scn.assemblMe_runningOperation

    del Scn.assemblme_copy_from_id

    del bpy.props.assemblme_preferences
    del bpy.props.assemblme_version
    del bpy.props.assemblme_module_path
    del bpy.props.assemblme_module_name

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
