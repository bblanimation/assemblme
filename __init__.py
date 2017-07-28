bl_info = {
    "name"        : "AssemblMe",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 0, 1),
    "blender"     : (2, 78, 0),
    "description" : "Iterative object assembly animations made simple",
    "location"    : "View3D > Tools > AssemblMe",
    # "wiki_url"    : "",
    "tracker_url" : "https://github.com/bblanimation/lego_add_ons/issues",
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
from .buttons.presets import animPresets
from bpy.types import Operator, AddonPreferences
props = bpy.props

class ExampleAddonPreferences(AddonPreferences):
    bl_idname = __name__

    addonPath = os.path.dirname(os.path.abspath(__file__))[:-10]
    defaultPresetsFP = os.path.join(addonPath, "assemblMe", "lib", "presets")
    presetsFilepath = StringProperty(
            name="Path to assemblMe presets",
            subtype='FILE_PATH',
            default=defaultPresetsFP)
    # number = IntProperty(
    #         name="Example Number",
    #         default=4,
    #         )
    # boolean = BoolProperty(
    #         name="Example Boolean",
    #         default=False,
    #         )

    # def draw(self, context):
    #     layout = self.layout
    #     layout.label(text="This is a preferences view for our addon")
    #     layout.prop(self, "filepath")
    #     layout.prop(self, "number")
    #     layout.prop(self, "boolean")


class OBJECT_OT_addon_prefs_example(Operator):
    """Display example preferences"""
    bl_idname = "object.addon_prefs_example"
    bl_label = "Addon Preferences Example"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        info = ("Path: %s, Number: %d, Boolean %r" %
                (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(OBJECT_OT_addon_prefs_example)
    bpy.utils.register_class(ExampleAddonPreferences)
    user_preferences = bpy.context.user_preferences
    props.addon_prefs = user_preferences.addons[__name__].preferences
    bpy.utils.register_module(__name__)

    props.addonVersion = "1.0.1"

    bpy.types.Scene.skipEmptySelections = BoolProperty(
        name="Skip Empty Selections",
        description="Skip frames where nothing is selected if checked",
        default=True)

    bpy.types.Scene.autoSaveOnCreateAnim = BoolProperty(
        name="Before 'Create Build Animation'",
        description="Save backup .blend file to project directory before executing 'Create Build Animation' actions",
        default=True)
    bpy.types.Scene.autoSaveOnStartOver = BoolProperty(
        name="Before 'Start Over'",
        description="Save backup .blend file to project directory before executing 'Start Over' actions",
        default=True)

    bpy.types.Scene.newPresetName = StringProperty(
        name="Name of New Preset",
        description="Full name of new custom preset",
        default="")

    presetNames = animPresets.getPresetTuples()
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

    # bpy.types.Scene.frameWithOrigLoc = IntProperty(
    #     default=-1)
    # bpy.types.Scene.animLength = IntProperty(
    #     default=0)
    # bpy.types.Scene.lastLayerVelocity = IntProperty(
    #     default=-1)
    # bpy.types.Scene.visualizerAnimated = BoolProperty(
    #     default=False)
    # bpy.types.Scene.visualizerLinked = BoolProperty(
    #     default=False)

    bpy.types.Scene.visualizerScale = FloatProperty(
        name="Scale",
        description="Scale of layer orientation visualizer",
        precision=1,
        min=0.1, max=100,
        default=10)

    bpy.types.Scene.visualizerNumCuts = FloatProperty(
        name="Num Cuts",
        description="Scale of layer orientation visualizer",
        precision=0,
        min=2, max=64,
        default=50)

    # list properties
    bpy.types.Scene.aglist = CollectionProperty(type=AssemblMe_AnimatedGroups)
    bpy.types.Scene.aglist_index = IntProperty(default=-1)

    # Session properties
    props.z_upper_bound = None
    props.z_lower_bound = None
    props.ignoredTypes = ["CAMERA", "LAMP", "POINT", "PLAIN_AXES", "EMPTY"]
    props.objMinLoc = 0
    props.objMaxLoc = 0

def unregister():
    Scn = bpy.types.Scene

    del Scn.visualizerNumCuts
    del Scn.visualizerScale
    del Scn.skipEmptySelections
    del Scn.aglist
    del Scn.aglist_index

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
