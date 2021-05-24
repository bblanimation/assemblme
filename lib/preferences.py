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

# System imports
import os

# Blender imports
import bpy
from bpy.props import *
from bpy.types import AddonPreferences

# Module imports
from ..ui import *
from ..operators import *

class ASSEMBLME_PT_preferences(AddonPreferences):
    # bl_idname = __name__
    bl_idname = __package__[:__package__.index(".lib")]


    def draw(self, context):
        layout = self.layout
