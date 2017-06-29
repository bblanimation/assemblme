bl_info = {
    "name"        : "AssemblMe",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 0, 0),
    "blender"     : (2, 78, 0),
    "description" : "Iterative object assembly animations made simple",
    "location"    : "View3D > Tools > AssemblMe",
    # "warning"     : "Work in progress",
    "wiki_url"    : "",
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
from bpy.props import *
from .ui import *
from .buttons import *
props = bpy.props

def register():
    bpy.utils.register_module(__name__)

    props.addonVersion = "1.0.0"

    bpy.types.Scene.firstFrame = IntProperty(
        name="Start",
        description="First frame of the (dis)assembly animation",
        min=0, max=500000,
        default=1)
    bpy.types.Scene.buildSpeed = FloatProperty(
        name="Step",
        description="Number of frames to skip forward between each object selection",
        unit="TIME",
        min=1, max=100,
        precision=0,
        default=1)
    bpy.types.Scene.objectVelocity = FloatProperty(
        name="Velocity",
        description="Speed of individual object layers (51 - Velocity = object animation duration in frames)",
        unit="VELOCITY",
        min=1, max=50,
        precision=0,
        default=45)

    bpy.types.Scene.layerHeight = FloatProperty(
        name="Layer Height",
        description="Height of the bounding box that selects objects for each frame in animation",
        unit="LENGTH",
        subtype="DISTANCE",
        min=.0001, max=50,
        precision=4,
        default=.1)

    bpy.types.Scene.xLocOffset = FloatProperty(
        name="X",
        description="Move objects by this x value",
        unit="LENGTH",
        precision=0,
        default=0)
    bpy.types.Scene.yLocOffset = FloatProperty(
        name="Y",
        description="Move objects by this y value",
        unit="LENGTH",
        precision=0,
        default=0)
    bpy.types.Scene.zLocOffset = FloatProperty(
        name="Z",
        description="Move objects by this z value",
        unit="LENGTH",
        precision=0,
        default=10)
    bpy.types.Scene.locationRandom = FloatProperty(
        name="Randomize",
        description="Randomize object location offset",
        min=0.0, max=100.0,
        precision=1,
        default=0.0)

    bpy.types.Scene.xRotOffset = FloatProperty(
        name="X",
        description="Rotate objects by this x value",
        unit="ROTATION",
        subtype="ANGLE",
        min=-360, max=360,
        precision=1, step=20,
        default=0)
    bpy.types.Scene.yRotOffset = FloatProperty(
        name="Y",
        description="Rotate objects by this y value",
        unit="ROTATION",
        subtype="ANGLE",
        min=-360, max=360,
        precision=1, step=20,
        default=0)
    bpy.types.Scene.zRotOffset = FloatProperty(
        name="Z",
        description="Rotate objects by this z value",
        unit="ROTATION",
        subtype="ANGLE",
        min=-360, max=360,
        precision=1, step=20,
        default=0)
    bpy.types.Scene.rotationRandom = FloatProperty(
        name="Randomize",
        description="Randomize object rotation offset",
        min=0.0, max=100.0,
        precision=1,
        default=0.0)

    interpolationModes = [("CONSTANT", "Constant", "Set interpolation mode for each object in assembly animation: Constant", "IPO_CONSTANT", 1),
                          ("LINEAR", "Linear", "Set interpolation mode for each object in assembly animation: Linear", "IPO_LINEAR", 2),
                          ("BEZIER", "Bezier", "Set interpolation mode for each object in assembly animation: Bezier", "IPO_BEZIER", 3),
                          ("SINE", "Sinusoidal", "Set interpolation mode for each object in assembly animation: Sinusoidal", "IPO_SINE", 4),
                          ("QUAD", "Quadratic", "Set interpolation mode for each object in assembly animation: Quadratic", "IPO_QUAD", 5),
                          ("CUBIC", "Cubic", "Set interpolation mode for each object in assembly animation: Cubic", "IPO_CUBIC", 6),
                          ("QUART", "Quartic", "Set interpolation mode for each object in assembly animation: Quartic", "IPO_QUART", 7),
                          ("QUINT", "Quintic", "Set interpolation mode for each object in assembly animation: Quintic", "IPO_QUINT", 8),
                          ("EXPO", "Exponential", "Set interpolation mode for each object in assembly animation: Exponential", "IPO_EXPO", 9),
                          ("CIRC", "Circular", "Set interpolation mode for each object in assembly animation: Circular", "IPO_CIRC", 10),
                          ("BACK", "Back", "Set interpolation mode for each object in assembly animation: Back", "IPO_BACK", 11),
                          ("BOUNCE", "Bounce", "Set interpolation mode for each object in assembly animation: Bounce", "IPO_BOUNCE", 12),
                          ("ELASTIC", "Elastic", "Set interpolation mode for each object in assembly animation: Elastic", "IPO_ELASTIC", 13)]

    bpy.types.Scene.locInterpolationMode = EnumProperty(
        name="Interpolation",
        description="Choose the interpolation mode for each objects' animation",
        items=interpolationModes,
        default="LINEAR")

    bpy.types.Scene.rotInterpolationMode = EnumProperty(
        name="Interpolation",
        description="Choose the interpolation mode for each objects' animation",
        items=interpolationModes,
        default="LINEAR")

    bpy.types.Scene.xOrient = FloatProperty(
        name="X",
        description="Objects assemble/disassemble at this angle",
        unit="ROTATION",
        subtype="ANGLE",
        min=-1.570796, max=1.570796,
        precision=1, step=20,
        default=0)
    bpy.types.Scene.yOrient = FloatProperty(
        name="Y",
        description="Objects assemble/disassemble at this angle",
        unit="ROTATION",
        subtype="ANGLE",
        min=-1.570796, max=1.570796,
        # min=-0.785398, max=0.785398,
        precision=1, step=10,
        default=0)
    bpy.types.Scene.orientRandom = FloatProperty(
        name="Random",
        description="Randomize object assembly/disassembly angle",
        min=0.0, max=100.0,
        precision=1,
        default=0.0)

    bpy.types.Scene.buildType = EnumProperty(
        name="Build Type",
        description="Choose whether to assemble or disassemble the objects",
        items=[("Assemble", "Assemble", "Assemble the objects to current location"),
              ("Disassemble", "Disassemble", "Disassemble objects from current location")],
        default="Assemble")
    bpy.types.Scene.invertBuild = BoolProperty(
        name="Assemble from other direction",
        description="Invert the animation so that the objects start (dis)assembling from the other side",
        default=False)

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
    bpy.types.Scene.printStatus = BoolProperty(
        name="Print Status in Terminal",
        description="Print out time remaining in terminal (disable for slight speed boost)",
        default=True)
    bpy.types.Scene.updateFrequency = IntProperty(
        name="Update Frequency",
        description="Minimum number of seconds to wait before printing status to terminal (increasing number may improve accuracy)",
        min=1, max=1440,
        default=5)

    bpy.types.Scene.animType = EnumProperty(
        name="Animation Preset",
        description="Choose the interpolation mode for each objects' animation",
        items=[("Custom", "Custom", "Create your own fully customized animation!"),
               ("Explode", "Explode", "Structure explodes; objects are sent off in random directions"),
               ("Standard Build", "Standard Build", "Objects fall straight down, one by one")],
        update=updateAnimType,
        default="Standard Build")

    bpy.types.Scene.frameWithOrigLoc = IntProperty(
        default=-1)

    bpy.types.Scene.animLength = IntProperty(
        default=0)
    bpy.types.Scene.lastLayerVelocity = IntProperty(
        default=-1)

    bpy.types.Scene.visualizerLinked = BoolProperty(
        default=False)

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



    # Session properties
    props.axisObj = None
    props.listZValues = []
    props.objects_to_move = []
    props.z_upper_bound = None
    props.z_lower_bound = None
    props.ignoredTypes = ["CAMERA", "LAMP", "POINT", "PLAIN_AXES", "EMPTY"]
    props.objMinLoc = 0
    props.objMaxLoc = 0

def unregister():
    Scn = bpy.types.Scene

    del Scn.visualizerNumCuts
    del Scn.visualizerScale
    del Scn.visualizerActive
    del Scn.lastLayerVelocity
    del Scn.animLength
    del Scn.frameWithOrigLoc
    del Scn.updateFrequency
    del Scn.printStatus
    del Scn.skipEmptySelections
    del Scn.invertBuild
    del Scn.buildType
    del Scn.orientRandom
    del Scn.yOrient
    del Scn.xOrient
    # del Scn.interpolationMode
    del Scn.rotationRandom
    del Scn.zRotOffset
    del Scn.yRotOffset
    del Scn.xRotOffset
    del Scn.locationRandom
    del Scn.zLocOffset
    del Scn.yLocOffset
    del Scn.xLocOffset
    del Scn.layerHeight
    del Scn.objectVelocity
    del Scn.buildSpeed
    del Scn.firstFrame

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
