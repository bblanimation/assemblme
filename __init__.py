# Copyright (C) 2019 Christopher Gearhart
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

bl_info = {
    "name"        : "AssemblMe",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 4, 0),
    "blender"     : (2, 83, 0),
    "description" : "Iterative object assembly animations made simple",
    "location"    : "View3D > Tools > AssemblMe",
    "warning"     : "",
    "wiki_url"    : "https://www.blendermarket.com/products/assemblme",
    "doc_url"     : "https://www.blendermarket.com/products/assemblme",  # 2.83+
    "tracker_url" : "https://github.com/bblanimation/assemblme/issues",
    "category"    : "Animation",
}

# System imports
import os
import getpass

# Blender imports
import bpy
from bpy.props import *
from bpy.types import Scene, Keyframe
from bpy.utils import register_class, unregister_class

# Addon import
from .functions import common, app_handlers, general, property_callbacks, timers
from .lib.classes_to_register import classes
from .lib import property_groups
from . import addon_updater_ops


def register():
    for cls in classes:
        common.make_annotations(cls)
        register_class(cls)

    bpy.props.assemblme_module_name = __name__
    bpy.props.assemblme_version = str(bl_info["version"])[1:-1]
    bpy.props.assemblme_developer_mode = getpass.getuser().startswith("cgear") and True
    bpy.props.assemblme_validated = True

    preset_names = general.get_preset_tuples(transfer_defaults=not bpy.app.background)
    Scene.anim_preset = EnumProperty(
        name="Presets",
        description="Stored AssemblMe presets",
        # items=[("None", "None", "")],
        items=preset_names,
        update=property_callbacks.update_anim_preset,
        default="None",
    )
    Scene.anim_preset_to_delete = EnumProperty(
        name="Preset to Delete",
        description="Another list of stored AssemblMe presets",
        # items=[("None", "None", "")],
        items=preset_names,
        default="None",
    )

    Scene.assemblme = PointerProperty(type=property_groups.AssemblMeProperties)

    # list properties
    Scene.aglist = CollectionProperty(type=property_groups.AnimatedCollectionProperties)
    Scene.aglist_index = IntProperty(default=-1, update=property_callbacks.ag_update)

    # register app handlers
    if common.b280():
        bpy.app.handlers.load_post.append(timers.register_assemblme_timers)
        bpy.app.timers.register(timers.handle_selections)
    else:
        bpy.app.handlers.scene_update_pre.append(app_handlers.handle_selections)
    bpy.app.handlers.load_post.append(app_handlers.convert_velocity_value)
    # bpy.app.handlers.load_pre.append(app_handlers.validate_assemblme)
    bpy.app.handlers.load_post.append(app_handlers.handle_upconversion)

    # addon updater code and configurations
    addon_updater_ops.register(bl_info)


def unregister():
    # addon updater unregister
    addon_updater_ops.unregister()

    # unregister app handlers
    bpy.app.handlers.load_post.remove(app_handlers.handle_upconversion)
    # bpy.app.handlers.load_pre.remove(app_handlers.validate_assemblme)
    bpy.app.handlers.load_post.remove(app_handlers.convert_velocity_value)
    if common.b280():
        if bpy.app.timers.is_registered(timers.handle_selections):
            bpy.app.timers.unregister(timers.handle_selections)
        bpy.app.handlers.load_post.remove(timers.register_assemblme_timers)
    else:
        bpy.app.handlers.scene_update_pre.remove(app_handlers.handle_selections)

    del Scene.aglist_index
    del Scene.aglist
    del Scene.assemblme
    del Scene.anim_preset_to_delete
    del Scene.anim_preset

    del bpy.props.assemblme_validated
    del bpy.props.assemblme_developer_mode
    del bpy.props.assemblme_version
    del bpy.props.assemblme_module_name

    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
