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
import math
from os.path import join, exists, split
import codecs

# Blender imports
import bpy
from bpy.app.handlers import persistent
from mathutils import Vector, Euler

# Module imports
from ..functions import *


@persistent
def convert_velocity_value(scn):
    if scn is None:
        return
    for ag in scn.aglist:
        if ag.object_velocity != -1:
            old_v = ag.object_velocity
            target_num_frames = 51 - old_v
            ag.velocity = 10 - (math.log(target_num_frames, 2))
            ag.object_velocity = -1


@persistent
def validate_assemblme(dummy):
    validated = False
    validation_file = join(get_addon_directory(), "lib", codecs.encode("nffrzoyzr_chepunfr_irevsvpngvba.gkg", "rot13"))
    if exists(validation_file):
        verification_str = "Thank you for supporting my work and ongoing development by purchasing BrickSculpt!\n"
        with open(validation_file) as f:
            validated = verification_str == codecs.encode(f.readline(), "rot13")
    if not validated:
        res = updater.run_update(
    		force=False,
			revert_tag="demo",
    		# callback=post_update_callback,
    		clean=False,
        )
        folderpath, foldername = split(get_addon_directory())
        bpy.props.assemblme_validated = False


@persistent
def handle_upconversion(scn):
    if scn is None:
        return
    # update storage scene name
    for ag in scn.aglist:
        if created_with_unsupported_version(ag):
            # convert from v1_1 to v1_2
            if int(ag.version[2]) < 2:
                if ag.collection and ag.collection.name.startswith("AssemblMe_animated_group"):
                    ag.collection.name = "AssemblMe_{}_group".format(ag.name)
            # convert from v1_2 to v1_3
            if int(ag.version[2]) < 2:
                collections = bpy.data.collections if b280() else bpy.data.groups
                ag.collection = collections.get(ag.group_name)
                # transfer props from 1_2 (camel to snake case)
                for prop in get_annotations(ag):
                    if prop.islower():
                        continue
                    snake_prop = camel_to_snake_case(prop)
                    if hasattr(ag, snake_prop):
                        setattr(ag, snake_prop, getattr(ag, prop))
