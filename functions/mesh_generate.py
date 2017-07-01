import bpy
import bmesh
import math
from mathutils import Matrix, Vector
from .__init__ import select

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
# r = radius, N = numVerts, h = height, co = target cylinder position
def makeCylinder(r, N, h, co=(0,0,0)):
    # create new bmesh object
    bme = bmesh.new()

    # create upper circle
    vertListT = []
    for i in range(N):
        vertListT.append(bme.verts.new((r * math.cos(((2 * math.pi) / N) * i), r * math.sin(((2 * math.pi) / N) * i), (h/2))))
    bme.faces.new(vertListT)

    # create lower circle
    vertListB = []
    for i in range(N):
        vertListB.append(bme.verts.new((r * math.cos(((2 * math.pi) / N) * i), r * math.sin(((2 * math.pi) / N) * i), -(h/2))))
    bme.faces.new(vertListB)

    bme.faces.new((vertListT[-1], vertListB[-1], vertListB[0], vertListT[0]))
    for v in range(N-1):
        bme.faces.new((vertListT.pop(0), vertListB.pop(0), vertListB[0], vertListT[0]))

    # send mesh to target location
    bme.transform(Matrix.Translation(Vector(co)))

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

def makeTruncIco():
    newObjFromBmesh(11, makeIco(), "truncated icosahedron")
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

def tupleAdd(p1, p2):
    """ returns linear sum of two given tuples """
    return tuple(x+y for x,y in zip(p1, p2))

# R = resolution, s = scale, o = offset lattice center from origin
def make2DLattice(R, s, o=(0,0,0)):
    # TODO: Raise exception if R is less than 2
    bme = bmesh.new()
    # initialize variables
    s = s/2
    R = int(R)
    inc = (s/R)*2
    vertMatrix = []
    for i in range(R+1):
        acc = -s
        vertList = []
        for j in range(R+1):
            # create and connect verts along x axis
            p = ( acc, (i * inc)-s, 0)
            v = bme.verts.new(tupleAdd(p, o))
            vertList.append(v)
            # create new edge parallel x axis
            if j != 0:
                e = bme.edges.new((vertList[j], vertList[j-1]))
            # increment accumulator
            acc += inc
        vertMatrix.append(vertList)
        # create new edge parallel to y axis
        if i != 0:
            for k in range(R+1):
                e = bme.edges.new((vertMatrix[i][k], vertMatrix[i-1][k]))
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
#         bpy.ops.object.delete(use_global=False)
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
#     makeTruncIco()
#     newObjFromBmesh(12, makeTorus(), "torus")
#     layerToOpen = 8
#
#     layerList = []
#     for i in range(20):
#         if i == layerToOpen-1: layerList.append(True)
#         else: layerList.append(False)
#     bpy.context.scene.layers = layerList
#
def getBrickSettings():
    """ returns dictionary containing brick detail settings """
    scn = bpy.context.scene
    settings = {}
    settings["underside"] = scn.undersideDetail
    settings["logo"] = scn.logoDetail
    settings["numStudVerts"] = scn.studVerts
    return settings

def make1x1(dimensions, refLogo, name='brick1x1'):
    """ create unlinked 1x1 LEGO Brick at origin """
    settings = getBrickSettings()

    bm = bmesh.new()
    cubeBM = makeCube(sX=dimensions["width"], sY=dimensions["width"], sZ=dimensions["height"])
    cylinderBM = makeCylinder(r=dimensions["stud_radius"], N=settings["numStudVerts"], h=dimensions["stud_height"], co=(0,0,dimensions["stud_offset"]))
    if refLogo:
        logoBM = bmesh.new()
        logoBM.from_mesh(refLogo.data)
        lw = dimensions["logo_width"]
        bmesh.ops.scale(logoBM, vec=Vector((lw, lw, lw)), verts=logoBM.verts)
        bmesh.ops.rotate(logoBM, verts=logoBM.verts, cent=(1.0, 0.0, 0.0), matrix=Matrix.Rotation(math.radians(90.0), 3, 'X'))
        bmesh.ops.translate(logoBM, vec=Vector((0, 0, dimensions["logo_offset"])), verts=logoBM.verts)
        # add logoBM mesh to bm mesh
        logoMesh = bpy.data.meshes.new('LEGOizer_tempMesh')
        logoObj = bpy.data.objects.new('LEGOizer_tempObj', logoMesh)
        bpy.context.scene.objects.link(logoObj)
        logoBM.to_mesh(logoMesh)
        select(logoObj, active=logoObj)
        if bpy.context.scene.logoResolution < 1:
            bpy.ops.object.modifier_add(type='DECIMATE')
            logoObj.modifiers['Decimate'].ratio = bpy.context.scene.logoResolution
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Decimate')
        bm.from_mesh(logoMesh)
        bpy.context.scene.objects.unlink(logoObj)
        bpy.data.objects.remove(logoObj)
        bpy.data.meshes.remove(logoMesh)

    # add cubeBM and cylinderBM meshes to bm mesh
    cube = bpy.data.meshes.new('legoizer_cube')
    cylinder = bpy.data.meshes.new('legoizer_cylinder')
    cubeBM.to_mesh(cube)
    cylinderBM.to_mesh(cylinder)
    bm.from_mesh(cube)
    bm.from_mesh(cylinder)
    bpy.data.meshes.remove(cube)
    bpy.data.meshes.remove(cylinder)

    # create apply mesh data to 'legoizer_brick1x1' data
    if bpy.data.objects.find(name) == -1:
        brick1x1Mesh = bpy.data.meshes.new(name + 'Mesh')
        brick1x1 = bpy.data.objects.new(name, brick1x1Mesh)
    else:
        brick1x1 = bpy.data.objects[name]
    bm.to_mesh(brick1x1.data)

    # return 'legoizer_brick1x1' object
    return brick1x1
