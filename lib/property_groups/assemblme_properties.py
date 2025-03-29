# Copyright (C) 2025 Christopher Gearhart
# chris@bricksbroughttolife.com
# http://bricksbroughttolife.com/
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

# System imports
# NONE!

# Blender imports
import bpy
from bpy.props import *
from bpy.types import PropertyGroup

# Module imports
from ...functions import *


class AssemblMeProperties(PropertyGroup):
    copy_from_id: IntProperty(default=-1)
    last_active_object_name: StringProperty(default="")

    new_preset_name: StringProperty(
        name="Name of New Preset",
        description="Full name of new custom preset",
        default="",
    )

    visualizer_scale: FloatProperty(
        name="Scale",
        description="Scale of layer orientation visualizer",
        subtype="DISTANCE",
        soft_min=0.1, soft_max=16,
        default=10,
    )
    visualizer_res: FloatProperty(
        name="Resolution",
        description="Resolution of layer orientation visualizer",
        precision=2,
        min=0.001, soft_min=0.05,
        soft_max=1,
        default=0.25,
    )
