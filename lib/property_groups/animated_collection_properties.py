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
# NONE!

# Blender imports
import bpy
from bpy.props import *
props = bpy.props

# Module imports
from ...functions import *

class AnimatedCollectionProperties(bpy.types.PropertyGroup):
    name = StringProperty(update=uniquify_name)
    id = IntProperty()
    idx = IntProperty()

    collection = PointerProperty(
        type=bpy.types.Collection if b280() else bpy.types.Group,
        name="Object Collection" if b280() else "Object Group",
        description="Group of objects to animate",
        update=collection_update,
    )

    anim_preset = EnumProperty(
        name="Presets",
        description="Stored AssemblMe presets",
        items=get_preset_tuples,
        update=update_anim_preset,
    )

    first_frame = IntProperty(
        name="Start",
        description="First frame of the (dis)assembly animation",
        min=0,
        max=500000,
        update=clear_preset,
        default=1,
    )
    build_speed = IntProperty(
        name="Step",
        description="Number of frames to skip forward between each object selection",
        min=1,
        soft_max=1000,
        update=clear_preset,
        default=1,
    )
    velocity = FloatProperty(
        name="Velocity",
        description="Speed of individual object layers (2^(10 - Velocity) = object animation duration in frames)",
        unit="VELOCITY",
        min=0.001,
        soft_max=100,
        step=1,
        update=clear_preset,
        default=6,
    )
    object_velocity = FloatProperty(default=-1)

    layer_height = FloatProperty(
        name="Layer Height",
        description="Height of the bounding box that selects objects for each layer in animation",
        unit="LENGTH",
        subtype="DISTANCE",
        min=0.0001,
        soft_max=1000,
        precision=4,
        update=clear_preset,
        default=0.1,
    )

    path_object = StringProperty(
        name="Path",
        description="Path object for animated objects to follow",
        default="",
    )

    loc_offset = FloatVectorProperty(
        name="Loc Offset",
        description="Move objects by this value",
        unit="LENGTH",
        subtype="XYZ",
        size=3,
        update=clear_preset,
        default=(0, 0, 10),
    )
    loc_random = FloatProperty(
        name="Randomize",
        description="Randomize object location offset",
        min=0,
        soft_max=10000,
        precision=1,
        update=clear_preset,
        default=0,
    )

    rot_offset = FloatVectorProperty(
        name="Z",
        description="Rotate objects by this z value (local space only)",
        unit="ROTATION",
        subtype="EULER",
        soft_min=-10000,
        soft_max=10000,
        step=20,
        size=3,
        update=clear_preset,
        default=(0, 0, 0),
    )
    rot_random = FloatProperty(
        name="Randomize",
        description="Randomize object rotation offset",
        min=0,
        soft_max=10000,
        precision=1,
        update=clear_preset,
        default=0,
    )

    interp_str = "Set interpolation mode for each object in assembly animation"
    interpolation_modes = [
        ("CONSTANT", "Constant", interp_str, "IPO_CONSTANT", 1),
        ("LINEAR", "Linear", interp_str, "IPO_LINEAR", 2),
        ("BEZIER", "Bezier", interp_str, "IPO_BEZIER", 3),
        ("SINE", "Sinusoidal", interp_str, "IPO_SINE", 4),
        ("QUAD", "Quadratic", interp_str, "IPO_QUAD", 5),
        ("CUBIC", "Cubic", interp_str, "IPO_CUBIC", 6),
        ("QUART", "Quartic", interp_str, "IPO_QUART", 7),
        ("QUINT", "Quintic", interp_str, "IPO_QUINT", 8),
        ("EXPO", "Exponential", interp_str, "IPO_EXPO", 9),
        ("CIRC", "Circular", interp_str, "IPO_CIRC", 10),
        ("BACK", "Back", interp_str, "IPO_BACK", 11),
        ("BOUNCE", "Bounce", interp_str, "IPO_BOUNCE", 12),
        ("ELASTIC", "Elastic", interp_str, "IPO_ELASTIC", 13),
    ]


    loc_interpolation_mode = EnumProperty(
        name="Interpolation",
        description="Choose the interpolation mode for each objects' animation",
        items=interpolation_modes,
        update=clear_preset,
        default="LINEAR",
    )

    rot_interpolation_mode = EnumProperty(
        name="Interpolation",
        description="Choose the interpolation mode for each objects' animation",
        items=interpolation_modes,
        update=clear_preset,
        default="LINEAR",
    )

    orient = FloatVectorProperty(
        name="Orientation",
        description="Orientation of the bounding box that selects objects for each layer in animation",
        unit="ROTATION",
        subtype="EULER",
        size=2,
        min=-1.570796, max=1.570796,
        # min=-0.785398, max=0.785398,
        precision=1, step=20,
        update=clear_preset,
        default=(0, 0),
    )
    orient_random = FloatProperty(
        name="Random",
        description="Randomize orientation of the bounding box that selects objects for each frame",
        min=0, max=100,
        precision=1,
        update=clear_preset,
        default=0,
    )

    build_type = EnumProperty(
        name="Build Type",
        description="Choose whether to assemble or disassemble the objects",
        items=[
            ("ASSEMBLE", "Assemble", "Assemble the objects to current location"),
            ("DISASSEMBLE", "Disassemble", "Disassemble objects from current location"),
        ],
        update=handle_outdated_preset,
        default="ASSEMBLE",
    )
    inverted_build = BoolProperty(
        name="From other direction",
        description="Invert the animation so that the objects start (dis)assembling from the other side",
        update=clear_preset,
        default=False,
    )

    use_global = BoolProperty(
        name="Use Global Orientation",
        description="Use global object orientation for creating animation (local orientation if disabled)",
        update=clear_preset,
        default=False,
    )
    mesh_only = BoolProperty(
        name="Mesh Objects Only",
        description="Non-mesh objects will be excluded from the animation",
        update=set_meshes_only,
        default=True,
    )
    skip_empty_selections = BoolProperty(
        name="Skip Empty Selections",
        description="Skip frames where nothing is selected if checked (Recommended)",
        update=clear_preset,
        default=True,
    )

    # Session properties
    obj_min_loc = FloatVectorProperty(subtype="XYZ", default=(0, 0, 0))
    obj_max_loc = FloatVectorProperty(subtype="XYZ", default=(0, 0, 0))

    animated = BoolProperty(default=False)
    anim_bounds_start = IntProperty(default=-1)
    anim_bounds_end = IntProperty(default=-1)
    time_created = FloatProperty(default=float("inf"))
    cur_preset = StringProperty(default="None")

    frame_with_orig_loc = IntProperty(default=-1)
    anim_length = IntProperty(default=0)
    last_layer_velocity = IntProperty(default=-1)
    visualizer_animated = BoolProperty(default=False)
    visualizer_active = BoolProperty(default=False)
    visualizer_needs_update = BoolProperty(default=False)

    last_active_object_name = StringProperty(default="")
    active_user_index = IntProperty(default=0)
    version = StringProperty(default="1.1.6")

    ### BACKWARDS COMPATIBILITY
    # v1.2
    firstFrame = IntProperty()
    buildSpeed = FloatProperty()
    objectVelocity = FloatProperty()
    layerHeight = FloatProperty()
    pathObject = StringProperty()
    locInterpolationMode = StringProperty(default="LINEAR")
    rotInterpolationMode = StringProperty(default="LINEAR")
    orientRandom = FloatProperty()
    buildType = StringProperty(default="ASSEMBLE")
    invertBuild = BoolProperty()
    useGlobal = BoolProperty()
    meshOnly = BoolProperty()
    skipEmptySelections = BoolProperty()
    frameWithOrigLoc = IntProperty()
    animLength = IntProperty()
    lastLayerVelocity = IntProperty()
    visualizerAnimated = BoolProperty()
    visualizerActive = BoolProperty()
    lastActiveObjectName = StringProperty()
    activeUserIndex = IntProperty()
