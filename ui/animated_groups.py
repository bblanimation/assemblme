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

import bpy
from bpy.props import IntProperty, CollectionProperty #, StringProperty
from bpy.types import Panel, UIList

# ui list item actions
class AssemblMe_Uilist_actions(bpy.types.Operator):
    bl_idname = "aglist.list_action"
    bl_label = "List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    # @classmethod
    # def poll(cls, context):
    #     """ ensures operator can execute (if not, returns false) """
    #     scn = context.scene
    #     for ag in scn.aglist:
    #         if ag.animated:
    #             return False
    #     return True

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.aglist_index

        try:
            item = scn.aglist[idx]
        except IndexError:
            pass

        if self.action == 'REMOVE':
            ag = scn.aglist[scn.aglist_index]
            if not ag.animated:
                scn.aglist_index -= 1
                scn.aglist.remove(idx)
                if scn.aglist_index == -1 and len(scn.aglist) > 0:
                    scn.aglist_index = 0
            else:
                self.report({"WARNING"}, 'Please delete the LEGOized model before attempting to remove this item.' % locals())

        if self.action == 'ADD':
            item = scn.aglist.add()
            last_index = scn.aglist_index
            scn.aglist_index = len(scn.aglist)-1
            item.name = "<New Animation>"
            item.id = len(scn.aglist)
            item.idx = len(scn.aglist)-1
            # if last_index == -1:
            #     item.startFrame = scn.frame_start
            #     item.stopFrame = min([scn.frame_start + 10, scn.frame_end])
            # else:
            #     matchProperties(scn.aglist[scn.aglist_index], scn.aglist[last_index])

        elif self.action == 'DOWN' and idx < len(scn.aglist) - 1:
            scn.aglist.move(scn.aglist_index, scn.aglist_index+1)
            scn.aglist_index += 1
            item.idx = scn.aglist_index

        elif self.action == 'UP' and idx >= 1:
            scn.aglist.move(scn.aglist_index, scn.aglist_index-1)
            scn.aglist_index -= 1
            item.idx = scn.aglist_index

        return {"FINISHED"}

# -------------------------------------------------------------------
# draw
# -------------------------------------------------------------------

# custom list
class AssemblMe_UL_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
        split = layout.split(0.9)
        split.prop(item, "name", text="", emboss=False, translate=False, icon='EDIT')

    def invoke(self, context, event):
        pass


# print button
class AssemblMe_Uilist_printAllItems(bpy.types.Operator):
    bl_idname = "aglist.print_list"
    bl_label = "Print List"
    bl_description = "Print all items to the console"

    def execute(self, context):
        scn = context.scene
        for i in scn.aglist:
            print (i.source_name, i.id)
        return{'FINISHED'}

# set source to active button
class AssemblMe_Uilist_setSourceGroupToActive(bpy.types.Operator):
    bl_idname = "aglist.set_to_active"
    bl_label = "Set to Active"
    bl_description = "Set group name to next group in active object"

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.aglist_index == -1:
            return False
        if context.scene.objects.active == None:
            return False
        if len(context.scene.objects.active.users_group) == 0:
            return False
        # ag = scn.aglist[scn.aglist_index]
        # n = ag.source_name
        # LEGOizer_source = "LEGOizer_%(n)s" % locals()
        # if groupExists(LEGOizer_source) and len(bpy.data.groups[LEGOizer_source].objects) == 1:
        #     return True
        # try:
        #     if bpy.data.objects[ag.source_name].type == 'MESH':
        #         return True
        # except:
        #     return False
        return True

    def execute(self, context):
        scn = context.scene
        ag = scn.aglist[scn.aglist_index]
        active_object = context.scene.objects.active
        if ag.lastActiveObjectName == active_object.name:
            ag.activeGroupIndex = (ag.activeGroupIndex + 1) % len(active_object.users_group)
        else:
            ag.lastActiveObjectName = active_object.name
            ag.activeGroupIndex = 0
        ag.group_name = active_object.users_group[ag.activeGroupIndex].name

        return{'FINISHED'}

# # select button
# class AssemblMe_Uilist_selectSource(bpy.types.Operator):
#     bl_idname = "aglist.select_source"
#     bl_label = "Select Source Object"
#     bl_description = "Select only source object for model"
#
#     @classmethod
#     def poll(cls, context):
#         """ ensures operator can execute (if not, returns false) """
#         scn = context.scene
#         if scn.aglist_index == -1:
#             return False
#         ag = scn.aglist[scn.aglist_index]
#         LEGOizer_source = "LEGOizer_%(n)s" % locals()
#         if groupExists(LEGOizer_source) and len(bpy.data.groups[LEGOizer_source].objects) == 1:
#             return True
#         try:
#             ag = scn.aglist[scn.aglist_index]
#             if bpy.data.objects[ag.ce_name].type == 'MESH':
#                 return True
#         except:
#             return False
#         return False
#
#     def execute(self, context):
#         scn = context.scene
#         ag = scn.aglist[scn.aglist_index]
#         n = ag.source_name
#         obj = bpy.data.objects[n]
#         select(obj, active=obj)
#
#         return{'FINISHED'}

# # select button
# class AssemblMe_Uilist_selectAllBricks(bpy.types.Operator):
#     bl_idname = "aglist.select_bricks"
#     bl_label = "Select Bricks"
#     bl_description = "Select only bricks in model"
#
#     @classmethod
#     def poll(cls, context):
#         """ ensures operator can execute (if not, returns false) """
#         scn = context.scene
#         if scn.aglist_index == -1:
#             return False
#         ag = scn.aglist[scn.aglist_index]
#         n = ag.source_name
#         LEGOizer_bricks = "LEGOizer_%(n)s_bricks" % locals()
#         if groupExists(LEGOizer_bricks) and len(bpy.data.groups[LEGOizer_bricks].objects) != 0:
#             return True
#         return False
#
#     def execute(self, context):
#         scn = context.scene
#         ag = scn.aglist[scn.aglist_index]
#         n = ag.source_name
#         LEGOizer_bricks = "LEGOizer_%(n)s_bricks" % locals()
#         if groupExists(LEGOizer_bricks):
#             objs = list(bpy.data.groups[LEGOizer_bricks].objects)
#             select(active=objs[0])
#             if len(objs) > 0:
#                 select(objs)
#
#         return{'FINISHED'}

# clear button
class AssemblMe_Uilist_clearAllItems(bpy.types.Operator):
    bl_idname = "aglist.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items in the list"

    def execute(self, context):
        scn = context.scene
        lst = scn.animatedGroupsCollection
        current_index = scn.aglist_index

        if len(lst) > 0:
             # reverse range to remove last item first
            for i in range(len(lst)-1,-1,-1):
                scn.animatedGroupsCollection.remove(i)
            self.report({'INFO'}, "All items removed")

        else:
            self.report({'INFO'}, "Nothing to remove")

        return{'FINISHED'}

def uniquifyName(self, context):
    """ if LEGO model exists with name, add '.###' to the end """
    scn = context.scene
    ag = scn.aglist[scn.aglist_index]
    name = ag.name
    while scn.aglist.keys().count(name) > 1:
        if name[-4] == ".":
            try:
                num = int(name[-3:])+1
            except:
                num = 1
            name = name[:-3] + "%03d" % (num)
        else:
            name = name + ".001"
    if ag.name != name:
        ag.name = name

# Create custom property group
class AssemblMe_AnimatedGroups(bpy.types.PropertyGroup):
    name = StringProperty(update=uniquifyName)
    id = IntProperty()
    idx = IntProperty()

    group_name = StringProperty(
        name="Object Group Name",
        description="Name of the source object to legoize (defaults to active object)",
        default="")

    firstFrame = IntProperty(
        name="Start",
        description="First frame of the (dis)assembly animation",
        min=0, max=500000,
        default=1)
    buildSpeed = FloatProperty(
        name="Step",
        description="Number of frames to skip forward between each object selection",
        unit="TIME",
        min=1, max=100,
        precision=0,
        default=1)
    objectVelocity = FloatProperty(
        name="Velocity",
        description="Speed of individual object layers (51 - Velocity = object animation duration in frames)",
        unit="VELOCITY",
        min=1, max=50,
        precision=0,
        default=45)

    layerHeight = FloatProperty(
        name="Layer Height",
        description="Height of the bounding box that selects objects for each frame in animation",
        unit="LENGTH",
        subtype="DISTANCE",
        min=.0001, max=50,
        precision=4,
        default=.1)

    pathObject = StringProperty(
        name="Path",
        description="Path object for animated objects to follow",
        default="")

    xLocOffset = FloatProperty(
        name="X",
        description="Move objects by this x value",
        unit="LENGTH",
        precision=0,
        default=0)
    yLocOffset = FloatProperty(
        name="Y",
        description="Move objects by this y value",
        unit="LENGTH",
        precision=0,
        default=0)
    zLocOffset = FloatProperty(
        name="Z",
        description="Move objects by this z value",
        unit="LENGTH",
        precision=0,
        default=10)
    locationRandom = FloatProperty(
        name="Randomize",
        description="Randomize object location offset",
        min=0.0, max=100.0,
        precision=1,
        default=0.0)

    xRotOffset = FloatProperty(
        name="X",
        description="Rotate objects by this x value",
        unit="ROTATION",
        subtype="ANGLE",
        min=-360, max=360,
        precision=1, step=20,
        default=0)
    yRotOffset = FloatProperty(
        name="Y",
        description="Rotate objects by this y value",
        unit="ROTATION",
        subtype="ANGLE",
        min=-360, max=360,
        precision=1, step=20,
        default=0)
    zRotOffset = FloatProperty(
        name="Z",
        description="Rotate objects by this z value",
        unit="ROTATION",
        subtype="ANGLE",
        min=-360, max=360,
        precision=1, step=20,
        default=0)
    rotationRandom = FloatProperty(
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


    locInterpolationMode = EnumProperty(
        name="Interpolation",
        description="Choose the interpolation mode for each objects' animation",
        items=interpolationModes,
        default="LINEAR")

    rotInterpolationMode = EnumProperty(
        name="Interpolation",
        description="Choose the interpolation mode for each objects' animation",
        items=interpolationModes,
        default="LINEAR")

    xOrient = FloatProperty(
        name="X",
        description="Objects assemble/disassemble at this angle",
        unit="ROTATION",
        subtype="ANGLE",
        min=-1.570796, max=1.570796,
        precision=1, step=20,
        default=0)
    yOrient = FloatProperty(
        name="Y",
        description="Objects assemble/disassemble at this angle",
        unit="ROTATION",
        subtype="ANGLE",
        min=-1.570796, max=1.570796,
        # min=-0.785398, max=0.785398,
        precision=1, step=10,
        default=0)
    orientRandom = FloatProperty(
        name="Random",
        description="Randomize object assembly/disassembly angle",
        min=0.0, max=100.0,
        precision=1,
        default=0.0)

    buildType = EnumProperty(
        name="Build Type",
        description="Choose whether to assemble or disassemble the objects",
        items=[("Assemble", "Assemble", "Assemble the objects to current location"),
              ("Disassemble", "Disassemble", "Disassemble objects from current location")],
        default="Assemble")
    invertBuild = BoolProperty(
        name="Assemble from other direction",
        description="Invert the animation so that the objects start (dis)assembling from the other side",
        default=False)

    animated = BoolProperty(default=False)

    ## DO THESE BELONG HERE??? ##
    frameWithOrigLoc = IntProperty(
        default=-1)
    animLength = IntProperty(
        default=0)
    lastLayerVelocity = IntProperty(
        default=-1)
    visualizerAnimated = BoolProperty(
        default=False)
    visualizerLinked = BoolProperty(
        default=False)

    lastActiveObjectName = StringProperty(default="")
    activeGroupIndex = IntProperty(default=0)

# -------------------------------------------------------------------
# register
# -------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.animatedGroupsCollection = CollectionProperty(type=AssemblMe_AnimatedGroups)
    bpy.types.Scene.aglist_index = IntProperty()

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.animatedGroupsCollection
    del bpy.types.Scene.aglist_index

if __name__ == "__main__":
    register()
