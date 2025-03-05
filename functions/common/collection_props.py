# Copyright (C) 2025 Christopher Gearhart
# christopher@bricksbroughttolife.com
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
import bpy

# Blender imports
from bpy.props import *

# Module imports
# NONE!


def get_collection_props(object):
    props_dict = dict()
    for attr_name in dir(object):
        if attr_name.startswith("__") or attr_name in ("bl_rna", "rna_type"):
            continue
        try:
            attr = getattr(object, attr_name)
        except AttributeError:
            continue
        if hasattr(type(attr), "__class__") and type(attr).__class__ == type(bpy.types.PropertyGroup):
            props_dict[attr_name] = get_collection_props(attr)
        else:
            props_dict[attr_name] = attr
    return props_dict


def set_collection_props(object, props_dict):
    for attr_name in props_dict:
        if attr_name.startswith("__") or attr_name in ("bl_rna", "rna_type"):
            continue
        try:
            attr = getattr(object, attr_name)
        except AttributeError:
            continue
        if hasattr(type(attr), "__class__") and type(attr).__class__ == type(bpy.types.PropertyGroup):  # is property group
            set_collection_props(attr, props_dict[attr_name])
        elif hasattr(attr, "add") and hasattr(attr, "remove"):  # is collection property
            for old_item in props_dict[attr_name]:
                sub_props_dict = get_collection_props(old_item)
                new_item = attr.add()
                set_collection_props(new_item, sub_props_dict)
        else:
            try:
                setattr(object, attr_name, props_dict[attr_name])
            except AttributeError:
                continue
