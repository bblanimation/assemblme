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
from bpy.types import Panel
from bpy.props import *
from ..functions import *
props = bpy.props

class ActionsPanel(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label       = "Actions"
    bl_idname      = "VIEW3D_PT_tools_AssemblMe_actions"
    bl_context     = "objectmode"
    bl_category    = "AssemblMe"
    COMPAT_ENGINES = {"CYCLES", "BLENDER_RENDER"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        col = layout.column(align=True)
        row = col.row(align=True)
        try:
            # if objects in 'AssemblMe_all_objects_moved' group set row to inactive (else set to active)
            animCreated = len(bpy.data.groups["AssemblMe_all_objects_moved"].objects) != 0
        except:
            # if 'AssemblMe_all_objects_moved' group does not exist, set row to active
            animCreated = False
        if not animCreated:
            row.operator("scene.create_build_animation", text="Create Build Animation", icon="EDIT")
        else:
            row.operator("scene.update_build_animation", text="Update Build Animation", icon="EDIT")
        row = col.row(align=True)
        row.operator("scene.start_over", text="Start Over", icon="RECOVER_LAST")
        if bpy.data.texts.find('AssemblMe_log') >= 0:
            split = layout.split(align=True, percentage = 0.9)
            col = split.column(align=True)
            row = col.row(align=True)
            row.operator("scene.report_error", text="Report Error", icon="URL")
            col = split.column(align=True)
            row = col.row(align=True)
            row.operator("scene.close_report_error", text="", icon="PANEL_CLOSE")

class SettingsPanel(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label       = "Settings"
    bl_idname      = "VIEW3D_PT_tools_AssemblMe_settings"
    bl_context     = "objectmode"
    bl_category    = "AssemblMe"
    COMPAT_ENGINES = {"CYCLES", "BLENDER_RENDER"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scn, "animType", text="Preset")

        box = layout.box()

        col = box.column(align=True)
        row = col.row(align=True)
        row.label("Animation:")
        row = col.row(align=True)
        row.operator("scene.refresh_build_animation_length", text="Duration: " + str(scn.animLength) + " frames", icon="FILE_REFRESH")
        row = col.row(align=True)
        row.prop(scn, "firstFrame")
        row = col.row(align=True)
        row.prop(scn, "buildSpeed")
        row = col.row(align=True)
        row.prop(scn, "objectVelocity")
        row = col.row(align=True)


        if scn.animType == "Custom":
            split = box.split(align=False, percentage = 0.5)
            col = split.column(align=True)
            row = col.row(align=True)
            row.label("Location Offset:")
            row = col.row(align=True)
            row.prop(scn, "xLocOffset")
            row = col.row(align=True)
            row.prop(scn, "yLocOffset")
            row = col.row(align=True)
            row.prop(scn, "zLocOffset")
            row = col.row(align=True)
            row.prop(scn, "locInterpolationMode", text="")
            row = col.row(align=True)
            row.prop(scn, "locationRandom")
            row = col.row(align=True)

            col = split.column(align=True)
            row = col.row(align=True)
            row.label("Rotation Offset:")
            row = col.row(align=True)
            row.prop(scn, "xRotOffset")
            row = col.row(align=True)
            row.prop(scn, "yRotOffset")
            row = col.row(align=True)
            row.prop(scn, "zRotOffset")
            row = col.row(align=True)
            row.prop(scn, "rotInterpolationMode", text="")
            row = col.row(align=True)
            row.prop(scn, "rotationRandom")
        elif scn.animType == "Standard Build":
            row = col.row(align=True)
            row.label("Location Offset:")
            row = col.row(align=True)
            row.prop(scn, "zLocOffset", text="Z")
            row = col.row(align=True)
            row.label("Interpolation:")
            row = col.row(align=True)
            row.prop(scn, "locInterpolationMode", text="")
            row = col.row(align=True)
            row.label("Layer Height:")
            row = col.row(align=True)
            row.prop(scn, "layerHeight", text="Z")
        elif scn.animType == "Explode":
            row = col.row(align=True)
            row.label("Location Offset:")
            row = col.row(align=True)
            row.prop(scn, "locInterpolationMode", text="")
            row = col.row(align=True)
            row.prop(scn, "locationRandom", text="Random Multiplier")
            row = col.row(align=True)
            row.label("Rotation Offset:")
            row = col.row(align=True)
            row.prop(scn, "rotInterpolationMode", text="")
            row = col.row(align=True)
            row.prop(scn, "rotationRandom", text="Random Multiplier")

        if scn.animType == "Custom":
            col1 = box.column(align=True)
            row = col1.row(align=True)
            row.label("Layer Orientation:")
            row = col1.row(align=True)
            split = row.split(align=True, percentage=0.9)
            row = split.row(align=True)
            col = row.column(align=True)
            col.prop(scn, "xOrient")
            col = row.column(align=True)
            col.prop(scn, "yOrient")
            col = split.column(align=True)
            if scn.visualizerLinked:
                col.operator("scene.visualize_layer_orientation", text="", icon="RESTRICT_VIEW_OFF")
            else:
                col.operator("scene.visualize_layer_orientation", text="", icon="RESTRICT_VIEW_ON")
            row = col1.row(align=True)
            row.prop(scn, "orientRandom")
            col1 = box.column(align=True)
            row = col1.row(align=True)
            row.prop(scn, "layerHeight")

            col = box.column(align=True)
            row = col.row(align=True)
            row.label("Build Type:")
            row = col.row(align=True)
            row.prop(scn, "buildType", text="")
            row = col.row(align=True)
            row.prop(scn, "invertBuild")

class AdvancedPanel(Panel):
    bl_space_type  = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label       = "Advanced"
    bl_idname      = "VIEW3D_PT_tools_AssemblMe_advanced"
    bl_context     = "objectmode"
    bl_category    = "AssemblMe"
    bl_options     = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"CYCLES", "BLENDER_RENDER"}

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(scn, "skipEmptySelections")
        row = col.row(align=True)
        row.prop(scn, "printStatus")
        if scn.printStatus:
            row = col.row(align=True)
            row.prop(scn, "updateFrequency")
            # layout.split()

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label("Auto Save:")
        row = col.row(align=True)
        row.prop(scn, "autoSaveOnCreateAnim")
        row = col.row(align=True)
        row.prop(scn, "autoSaveOnStartOver")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label("Visualizer:")
        row = col.row(align=True)
        row.prop(scn, "visualizerScale")
        row.prop(scn, "visualizerNumCuts")
