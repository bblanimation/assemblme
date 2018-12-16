# Copyright (C) 2018 Christopher Gearhart
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
import numpy as np

# Blender imports
import bpy
import bmesh

def newObjFromBmesh(layer, bme, meshName, objName=None, loc=(0,0,0), edgeSplit=True):
    scn = bpy.context.scene
    # if only one name given, use it for both names
    objName = objName or meshName

    # create mesh and object
    me = bpy.data.meshes.new(meshName)
    ob = bpy.data.objects.new(objName, me)
    # move object to target location
    ob.location = loc
    # link and select object
    scn.collection.objects.link(ob)
    scn.update()

    # send bmesh data to object data
    bme.to_mesh(me)
    ob.data.update()

    # add edge split modifier
    if edgeSplit:
        addEdgeSplitMod(ob)

    # move to appropriate layer
    layerList = [i == layer - 1 for i in range(20)]
    ob.layers = layerList

    return ob

def main():
    # try to delete existing objects
    delete(bpy.data.objects)

    # create objects
    newObjFromBmesh(1, makeSquare(), "square")
    newObjFromBmesh(2, makeCircle(1, 10, 0), "circle")
    newObjFromBmesh(3, makeCube(), "cube")
    newObjFromBmesh(4, makeTetra(), "tetrahedron")
    newObjFromBmesh(5, makeCylinder(1, 10, 5), "cylinder")
    newObjFromBmesh(6, makeCone(1, 10), "cone")
    newObjFromBmesh(7, makeOcta(), "octahedron")
    newObjFromBmesh(8, makeDodec(), "dodecahedron")
    newObjFromBmesh(9, makeUVSphere(1, 16, 10), "sphere")
    newObjFromBmesh(10, makeIco(), "icosahedron")
    makeTruncIco(11)
    newObjFromBmesh(12, makeTorus(), "torus")
    newObjFromBmesh(13, makeLattice((1,1,1), (10,20,10), (0,0,0)), "lattice")
    openLayer(13)

# main()
