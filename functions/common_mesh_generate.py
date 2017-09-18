import bpy
import bmesh
import math
import numpy as np
from mathutils import Matrix, Vector

def makeSquare():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    v1 = bme.verts.new(( 1, 1, 0))
    v2 = bme.verts.new((-1, 1, 0))
    v3 = bme.verts.new((-1,-1, 0))
    v4 = bme.verts.new(( 1,-1, 0))
    # bme.verts.ensure_lookup_table()
    bme.faces.new((v1, v2, v3, v4))

    # return bmesh
    return bme
# r = radius, N = numVerts, z = axis to form circle on
def makeCircle(r, N, z):
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    vertList = []
    for i in range(N):
        vertList.append(bme.verts.new((r * math.cos(((2 * math.pi) / N) * i), r * math.sin(((2 * math.pi) / N) * i), z)))
    bme.faces.new(vertList)

    # return bmesh
    return bme
# sX = X scale, sY = Y scale, sZ = Z scale
def makeCube(sX=1, sY=1, sZ=1):
    # create new bmesh object
    bme = bmesh.new()

    # half scale inputs
    sX = sX/2
    sY = sY/2
    sZ = sZ/2

    # do modifications here
    v1 = bme.verts.new(( sX, sY, sZ))
    v2 = bme.verts.new((-sX, sY, sZ))
    v3 = bme.verts.new((-sX,-sY, sZ))
    v4 = bme.verts.new(( sX,-sY, sZ))
    bme.faces.new((v1, v2, v3, v4))
    v5 = bme.verts.new(( sX, sY,-sZ))
    v6 = bme.verts.new((-sX, sY,-sZ))
    bme.faces.new((v2, v1, v5, v6))
    v7 = bme.verts.new((-sX,-sY,-sZ))
    bme.faces.new((v3, v2, v6, v7))
    v8 = bme.verts.new(( sX,-sY,-sZ))
    bme.faces.new((v1, v4, v8, v5))
    bme.faces.new((v4, v3, v7, v8))
    bme.faces.new((v8, v7, v6, v5))

    # return bmesh
    return bme

def makeTetra():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    v1 = bme.verts.new((0, 1, -1))
    v2 = bme.verts.new((0.86603, -0.5, -1))
    v3 = bme.verts.new((-0.86603, -0.5, -1))
    bme.faces.new((v1, v2, v3))
    v4 = bme.verts.new((0, 0, 1))
    bme.faces.new((v4, v3, v2))
    bme.faces.new((v4, v1, v3))
    bme.faces.new((v4, v2, v1))

    # return bmesh
    return bme
# r = radius, N = numVerts, h = height, co = target cylinder position, botFace = Bool for creating face on bottom, bme = bmesh to insert mesh data into
def makeCylinder(r, N, h, co=(0,0,0), botFace=True, bme=None):
    # create new bmesh object
    if bme == None:
        bme = bmesh.new()

    # create upper and lower circles
    vertListT = []
    vertListB = []
    for i in range(N):
        x = r * math.cos(((2 * math.pi) / N) * i)
        y = r * math.sin(((2 * math.pi) / N) * i)
        z = h / 2
        coordT = (x + co[0], y + co[1], z + co[2])
        coordB = (x + co[0], y + co[1], -z + co[2])
        vertListT.append(bme.verts.new(coordT))
        vertListB.append(bme.verts.new(coordB))

    # create top and bottom faces
    bme.faces.new(vertListT)
    if botFace:
        bme.faces.new(vertListB)

    # create faces on the sides
    bme.faces.new((vertListT[-1], vertListB[-1], vertListB[0], vertListT[0]))
    for v in range(N-1):
        bme.faces.new((vertListT.pop(0), vertListB.pop(0), vertListB[0], vertListT[0]))

    # return bmesh
    return bme
# r = radius, N = numVerts
def makeCone(r, N):
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    topV = bme.verts.new((0, 0, 1))
    # create bottom circle
    vertList = []
    for i in range(N):
        vertList.append(bme.verts.new((r * math.cos(((2 * math.pi) / N) * i), r * math.sin(((2 * math.pi) / N) * i), -1)))
    bme.faces.new(vertList)

    bme.faces.new((vertList[-1], vertList[0], topV))
    for v in range(N-1):
        bme.faces.new((vertList.pop(0), vertList[0], topV))


    # return bmesh
    return bme

def makeOcta():
    # create new bmesh object
    bme = bmesh.new()

    # make vertices
    topV = bme.verts.new((0, 0, 1.5))
    botV = bme.verts.new((0, 0,-1.5))

    v1 = bme.verts.new(( 1, 1, 0))
    v2 = bme.verts.new((-1, 1, 0))
    v3 = bme.verts.new((-1,-1, 0))
    v4 = bme.verts.new(( 1,-1, 0))

    # make faces
    bme.faces.new((topV, v1, v2))
    bme.faces.new((botV, v2, v1))
    bme.faces.new((topV, v2, v3))
    bme.faces.new((botV, v3, v2))
    bme.faces.new((topV, v3, v4))
    bme.faces.new((botV, v4, v3))
    bme.faces.new((topV, v4, v1))
    bme.faces.new((botV, v1, v4))

    # return bmesh
    return bme

def makeDodec():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    q = 1.618
    bme.verts.new((   1,   1,   1))
    bme.verts.new((  -1,  -1,  -1))
    bme.verts.new((  -1,   1,   1))
    bme.verts.new((   1,  -1,   1))
    bme.verts.new((   1,   1,  -1))
    bme.verts.new((   1,  -1,  -1))
    bme.verts.new((  -1,  -1,   1))
    bme.verts.new((  -1,   1,  -1))
    bme.verts.new((   0, 1/q,   q))
    bme.verts.new((   0,-1/q,   q))
    bme.verts.new((   0, 1/q,  -q))
    bme.verts.new((   0,-1/q,  -q))
    bme.verts.new(( 1/q,   q,   0))
    bme.verts.new(( 1/q,  -q,   0))
    bme.verts.new((-1/q,   q,   0))
    bme.verts.new((-1/q,  -q,   0))
    bme.verts.new((   q,   0, 1/q))
    bme.verts.new((  -q,   0, 1/q))
    bme.verts.new((   q,   0,-1/q))
    bme.verts.new((  -q,   0,-1/q))


    # return bmesh
    return bme
# r = radius, V = numVerticalCircles, H = numHorizontalCircles
def makeUVSphere(r, V, H):
    # create new bmesh object
    bme = bmesh.new()
    testBme = bmesh.new()

    # create vertices
    vertListV = []
    vertListH = []
    for i in range(int(V/4), int((3*V)/4)+1):
        v = testBme.verts.new((r * math.cos(((2 * math.pi) / V) * i), 0, r * math.sin(((2 * math.pi) / V) * i)))
        vertListV.append(v)
        nextVertListH = []
        if i != int(V/4) and i != int((3*V)/4):
            for j in range(H):
                # replace 'r' with x value of 'v'
                nextVertListH.append(bme.verts.new((v.co.x * math.cos(((2 * math.pi) / H) * j), v.co.x * math.sin(((2 * math.pi) / H) * j), v.co.z)))
            vertListH.append(nextVertListH)
        elif i == int(V/4):
            topV = bme.verts.new((v.co))
        elif i == int((3*V)/4):
            botV = bme.verts.new((v.co))

    # create faces
    for l in range(len(vertListH)-1):
        for m in range(-1, len(vertListH[l])-1):
            bme.faces.new((vertListH[l][m], vertListH[l+1][m], vertListH[l+1][m+1], vertListH[l][m+1]))

    # create top and bottom faces
    for n in range(-1,H-1):
        bme.faces.new((vertListH[0][n], vertListH[0][n+1], topV))
        bme.faces.new((vertListH[-1][n+1], vertListH[-1][n], botV))


    # return bmesh
    return bme

def makeIco():
    # create new bmesh object
    bme = bmesh.new()

    # do modifications here
    topV = bme.verts.new((0, 0, 1))
    r1a = bme.verts.new((0.28, 0.85, 0.45))
    r1b = bme.verts.new((-0.72, 0.53, 0.45))
    bme.faces.new((r1a, r1b, topV))
    r1c = bme.verts.new((-0.72, -0.53, 0.45))
    bme.faces.new((r1b, r1c, topV))
    r1d = bme.verts.new((0.28, -0.85, 0.45))
    bme.faces.new((r1c, r1d, topV))
    r1e = bme.verts.new((0.89, 0, 0.45))
    bme.faces.new((r1d, r1e, topV))
    bme.faces.new((r1e, r1a, topV))
    botV = bme.verts.new((0, 0,-1))
    r2a = bme.verts.new((0.72, 0.53, -0.45))
    r2b = bme.verts.new((-0.28, 0.85, -0.45))
    bme.faces.new((r2b, r2a, botV))
    r2c = bme.verts.new((-0.89, 0, -0.45))
    bme.faces.new((r2c, r2b, botV))
    r2d = bme.verts.new((-0.28, -0.85, -0.45))
    bme.faces.new((r2d, r2c, botV))
    r2e = bme.verts.new((0.72, -0.53, -0.45))
    bme.faces.new((r2e, r2d, botV))
    bme.faces.new((r2a, r2e, botV))

    bme.faces.new((r2a, r2b, r1a))
    bme.faces.new((r2b, r2c, r1b))
    bme.faces.new((r2c, r2d, r1c))
    bme.faces.new((r2d, r2e, r1d))
    bme.faces.new((r2e, r2a, r1e))

    bme.faces.new((r1a, r2b, r1b))
    bme.faces.new((r1b, r2c, r1c))
    bme.faces.new((r1c, r2d, r1d))
    bme.faces.new((r1d, r2e, r1e))
    bme.faces.new((r1e, r2a, r1a))

    # return bmesh
    return bme

def makeTruncIco(layer):
    newObjFromBmesh(layer, makeIco(), "truncated icosahedron")
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.bevel(offset=0.35, vertex_only=True)
    bpy.ops.object.editmode_toggle()

def makeTorus():
    # create new bmesh object
    bme = bmesh.new()
    testBme = bmesh.new()

    # create reference circle
    vertList = []
    # for i in range(N):
    #     vertList.append(testBme.verts.new((r * math.cos(((2 * math.pi) / N) * i), r * math.sin(((2 * math.pi) / N) * i), z)))




    # return bmesh
    return bme

def tupleAdd(p1, p2):
    """ returns linear sum of two given tuples """
    return tuple(x+y for x,y in zip(p1, p2))



# R = resolution, s = 3D scale tuple, o = offset lattice center from origin
def makeLattice(R, s, o=(0,0,0)):
    # TODO: Raise exception if R is less than 2
    bme = bmesh.new()
    # initialize variables
    vertMatrix = []
    xR = R[0]
    yR = R[1]
    zR = R[2]
    xS = s[0]
    yS = s[1]
    zS = s[2]
    xL = int(round((xS)/xR))+1
    if xL != 1: xL += 1
    yL = int(round((yS)/yR))+1
    if yL != 1: yL += 1
    zL = int(round((zS)/zR))+1
    if zL != 1: zL += 1
    # iterate through x,y,z dimensions and create verts/connect with edges
    for x in range(xL):
        vertList1 = []
        xCO = (x-(xS/(2*xR)))*xR
        for y in range(yL):
            vertList2 = []
            yCO = (y-(yS/(2*yR)))*yR
            for z in range(zL):
                # create verts
                zCO = (z-(zS/(2*zR)))*zR
                p = (xCO, yCO, zCO)
                v = bme.verts.new(tupleAdd(p, o))
                vertList2.append(v)
                # create new edge parallel x axis
                if z != 0:
                    e = bme.edges.new((vertList2[z], vertList2[z-1]))
            vertList1.append(vertList2)
            if y != 0:
                for z in range(zL):
                    e = bme.edges.new((vertList1[y][z], vertList1[y-1][z]))
        vertMatrix.append(vertList1)
        if x != 0:
            for y in range(yL):
                for z in range(zL):
                    e = bme.edges.new((vertMatrix[x][y][z], vertMatrix[x-1][y][z]))
    # return bmesh
    return bme

# R = resolution, s = scale
def makeSimple2DLattice(R, s):
    # TODO: Raise exception if R is less than 2
    # create new bmesh object
    bme = bmesh.new()
    # divide scale by 2
    s = s/2
    # convert R to integer
    R = int(R)
    # initialize incrementor and accumulator
    inc = (s/R)*2
    acc = -s
    for i in range(R+1):
        # create and connect verts along x axis
        t = bme.verts.new(( acc,  s, 0))
        b = bme.verts.new(( acc, -s, 0))
        e1 = bme.edges.new((t, b))
        # create and connect verts along y axis
        r = bme.verts.new((  s, acc, 0))
        l = bme.verts.new(( -s, acc, 0))
        e2 = bme.edges.new((r, l))
        # increment accumulator
        acc += inc
    # return bmesh
    return bme

# def newObjFromBmesh(layer, bme, meshName, objName=False):
#
#     # if only one name given, use it for both names
#     if not objName:
#         objName = meshName
#
#     # create mesh and object
#     me = bpy.data.meshes.new(meshName)
#     ob = bpy.data.objects.new(objName, me)
#
#     scn = bpy.context.scene # grab a reference to the scene
#     scn.objects.link(ob)    # link new object to scene
#     scn.objects.active = ob # make new object active
#     ob.select = True        # make new object selected (does not deselect
#                             # other objects)
#
#     obj = bme.to_mesh(me)         # push bmesh data into me
#
#     # move to appropriate layer
#     layerList = []
#     for i in range(20):
#         if i == layer-1:
#             layerList.append(True)
#         else:
#             layerList.append(False)
#     bpy.ops.object.move_to_layer(layers=layerList)
#     bpy.context.scene.layers = layerList
#     bpy.ops.object.select_all(action='TOGGLE')
#
# def deleteExisting():
#     # delete existing objects
#     tmpList = [True]*20
#     bpy.context.scene.layers = tmpList
#     for i in range(2):
#         bpy.ops.object.select_all(action='TOGGLE')
#         bpy.ops.object.delete()
#     bpy.context.scene.layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True]
#
# def main():
#     deleteExisting()
#
#     # create objects
#     newObjFromBmesh(1, makeSquare(), "square")
#     newObjFromBmesh(2, makeCircle(1, 10, 0), "circle")
#     newObjFromBmesh(3, makeCube(), "cube")
#     newObjFromBmesh(4, makeTetra(), "tetrahedron")
#     newObjFromBmesh(5, makeCylinder(1, 10, 5), "cylinder")
#     newObjFromBmesh(6, makeCone(1, 10), "cone")
#     newObjFromBmesh(7, makeOcta(), "octahedron")
#     newObjFromBmesh(8, makeDodec(), "dodecahedron")
#     newObjFromBmesh(9, makeUVSphere(1, 16, 10), "sphere")
#     newObjFromBmesh(10, makeIco(), "icosahedron")
#     makeTruncIco(11)
#     newObjFromBmesh(12, makeTorus(), "torus")
#     newObjFromBmesh(13, makeLattice((1,1,1), (10,20,10), (0,0,0)), "lattice")
#     layerToOpen = 13
#
#     layerList = []
#     for i in range(20):
#         if i == layerToOpen-1: layerList.append(True)
#         else: layerList.append(False)
#     bpy.context.scene.layers = layerList
#
# main()
