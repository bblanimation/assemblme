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

# r = radius, N = numVerts, h = height, t = thickness, co = target cylinder position
def makeTube(r, N, h, t, co=(0,0,0), bme=None):
    # create new bmesh object
    if bme == None:
        bme = bmesh.new()

    # create upper and lower circles
    vertListTInner = []
    vertListBInner = []
    vertListTOuter = []
    vertListBOuter = []
    for i in range(N):
        # set coord x,y,z locations
        xInner = r * math.cos(((2 * math.pi) / N) * i)
        xOuter = (r + t) * math.cos(((2 * math.pi) / N) * i)
        yInner = r * math.sin(((2 * math.pi) / N) * i)
        yOuter = (r + t) * math.sin(((2 * math.pi) / N) * i)
        z = h / 2
        # inner cylinder verts
        coordT = (xInner + co[0], yInner + co[1], z + co[2])
        coordB = (xInner + co[0], yInner + co[1], -z + co[2])
        vertListTInner.append(bme.verts.new(coordT))
        vertListBInner.append(bme.verts.new(coordB))
        # outer cylinder verts
        coordT = (xOuter + co[0], yOuter + co[1], z + co[2])
        coordB = (xOuter + co[0], yOuter + co[1], -z + co[2])
        vertListTOuter.append(bme.verts.new(coordT))
        vertListBOuter.append(bme.verts.new(coordB))
        # create faces between them
        if i > 0:
            bme.faces.new((vertListBOuter[-2], vertListBInner[-2], vertListBInner[-1], vertListBOuter[-1]))
    bme.faces.new((vertListBOuter[-1], vertListBInner[-1], vertListBInner[0], vertListBOuter[0]))

    # create faces on the outer and inner sides
    bme.faces.new((vertListTOuter[-1], vertListBOuter[-1], vertListBOuter[0], vertListTOuter[0]))
    bme.faces.new((vertListTInner[0], vertListBInner[0], vertListBInner[-1], vertListTInner[-1]))
    for v in range(N-1):
        bme.faces.new((vertListTOuter.pop(0), vertListBOuter.pop(0), vertListBOuter[0], vertListTOuter[0]))
        bme.faces.new((vertListTInner[1], vertListBInner[1], vertListBInner.pop(0), vertListTInner.pop(0)))

    # return bmesh
    return bme

# r = radius, N = numVerts, h = height, o = z offset, co = target cylinder position, bme = bmesh to insert mesh data into
def makeInnerCylinder(r, N, h, co=(0,0,0), bme=None):
    """ Make a brick inner cylinder """
    # create upper circle
    vertListT = []
    vertListB = []
    vertListBDict = {"++":[], "-+":[], "--":[], "+-":[], "x+":[], "x-":[], "y+":[], "y-":[]}
    for i in range(N):
        # set coord x,y,z locations
        x = r * math.cos(((2 * math.pi) / N) * i)
        y = r * math.sin(((2 * math.pi) / N) * i)
        z = co[2]
        # create top verts
        vertListT.append(bme.verts.new((x + co[0], y + co[1], z + h)))

        # create bottom verts and add to dict
        v = bme.verts.new((x + co[0], y + co[1], z))
        yP = v.co.y > co[1] # true if 'y' is positive
        xP = v.co.x > co[0] # true if 'x' is positive
        if abs(v.co.x - co[0]) < 0.00001:
            print("x success")
            if yP:
                l = "y+"
            else:
                l = "y-"
        elif abs(v.co.y - co[1]) < 0.00001:
            print("y success")
            if xP:
                l = "x+"
            else:
                l = "x-"
        else:
            if xP and yP:
                l = "++"
            elif not xP and yP:
                l = "-+"
            elif not xP and not yP:
                l = "--"
            else:
                l = "+-"
        vertListBDict[l].insert(0,v)
        vertListB.append(v)
    bme.faces.new(vertListT[::-1])

#    # create lower circle faces with square
#    lastKey = "x-y"
#    for key in ["xy", "-xy", "-x-y", "x-y"]:
#        bme.faces.new((vertListBDict[lastKey][1][-1], vertListBDict[key][1][0], vertListBDict[key][0], vertListBDict[lastKey][0]))
#        for i in range(1, len(vertListBDict[key][1])):
#            bme.faces.new((vertListBDict[key][1][i-1], vertListBDict[key][1][i], vertListBDict[key][0]))
#        lastKey = key

    bme.faces.new((vertListT[-1], vertListB[-1], vertListB[0], vertListT[0]))
    for v in range(N-1):
        bme.faces.new((vertListT[1], vertListB[1], vertListB.pop(0), vertListT.pop(0)))

    return vertListBDict

def makeBrick(dimensions, brickSize, numStudVerts=None, detail="Low Detail"):
    # create new bmesh object
    bme = bmesh.new()

    # set scale and thickness variables
    dX = dimensions["width"]
    dY = dimensions["width"]
    dZ = dimensions["height"]
    thick = dimensions["thickness"]
    sX = (brickSize[0] * 2) - 1
    sY = (brickSize[1] * 2) - 1

    # half scale inputs
    dX = dX/2
    dY = dY/2
    dZ = dZ/2

    # CREATING CUBE
    v1 = bme.verts.new(( dX * sX, dY * sY, dZ))
    v2 = bme.verts.new((-dX, dY * sY, dZ))
    v3 = bme.verts.new((-dX,-dY, dZ))
    v4 = bme.verts.new(( dX * sX,-dY, dZ))
    bme.faces.new((v1, v2, v3, v4))
    v5 = bme.verts.new(( dX * sX, dY * sY,-dZ))
    v6 = bme.verts.new((-dX, dY * sY,-dZ))
    bme.faces.new((v2, v1, v5, v6))
    v7 = bme.verts.new((-dX,-dY,-dZ))
    bme.faces.new((v3, v2, v6, v7))
    v8 = bme.verts.new(( dX * sX,-dY,-dZ))
    bme.faces.new((v1, v4, v8, v5))
    bme.faces.new((v4, v3, v7, v8))

    # CREATING STUD(S)
    studInset = thick * 0.9
    for xNum in range(brickSize[0]):
        for yNum in range(brickSize[1]):
            makeCylinder(r=dimensions["stud_radius"], N=numStudVerts, h=dimensions["stud_height"]+studInset, co=(xNum*dX*2,yNum*dY*2,dimensions["stud_offset"]-(studInset/2)), botFace=False, bme=bme)

    if detail == "Flat":
        bme.faces.new((v8, v7, v6, v5))
    else:
        # creating cylinder
        # making verts for hollow portion at bottom
        v9 = bme.verts.new((v5.co.x-thick, v5.co.y-thick, v5.co.z))
        v10 = bme.verts.new((v6.co.x+thick, v6.co.y-thick, v6.co.z))
        bme.faces.new((v5, v9, v10, v6))
        v11 = bme.verts.new((v7.co.x+thick, v7.co.y+thick, v7.co.z))
        bme.faces.new((v6, v10, v11, v7))
        v12 = bme.verts.new((v8.co.x-thick, v8.co.y+thick, v8.co.z))
        bme.faces.new((v7, v11, v12, v8))
        bme.faces.new((v8, v12, v9, v5))
        # making verts for hollow portion at top
        v13 = bme.verts.new((v9.co.x, v9.co.y, v1.co.z-thick))
        v14 = bme.verts.new((v10.co.x, v10.co.y, v2.co.z-thick))
        bme.faces.new((v9, v13, v14, v10))
        v15 = bme.verts.new((v11.co.x, v11.co.y, v3.co.z-thick))
        bme.faces.new((v10, v14, v15, v11))
        v16 = bme.verts.new((v12.co.x, v12.co.y, v4.co.z-thick))
        bme.faces.new((v11, v15, v16, v12))
        bme.faces.new((v12,v16, v13, v9))
        # make tubes
        for xNum in range(brickSize[0]-1):
            for yNum in range(brickSize[1]-1):
                makeTube(dimensions["stud_radius"], numStudVerts, (dZ*2)-thick, dimensions["tube_thickness"], co=((xNum * dX * 2) + dX, (yNum * dY * 2) + dY, -thick/2), bme=bme)
        # make face at top
        if detail == "Low Detail":
            bme.faces.new((v16, v15, v14, v13))
        # make small inner cylinder at top
        elif detail == "High Detail":
            botVertsDofDs = {}
            for xNum in range(brickSize[0]):
                for yNum in range(brickSize[1]):
                    r = dimensions["stud_radius"]-(2 * thick)
                    N = numStudVerts
                    h = thick * 0.99
                    botVertsD = makeInnerCylinder(r, N, h, co=(xNum*dX*2,yNum*dY*2,v16.co.z), bme=bme)
                    botVertsDofDs["%(xNum)s,%(yNum)s" % locals()] = botVertsD

            # Make corner faces
            vList = botVertsDofDs["0,0"]["y-"] + botVertsDofDs["0,0"]["--"] + botVertsDofDs["0,0"]["x-"]
            for i in range(1, len(vList)):
                bme.faces.new((vList[i], vList[i-1], v15))
            vList = botVertsDofDs[str(xNum) + "," + str(0)]["x+"] + botVertsDofDs[str(xNum) + "," + str(0)]["+-"] + botVertsDofDs[str(xNum) + "," + str(0)]["y-"]
            for i in range(1, len(vList)):
                bme.faces.new((vList[i], vList[i-1], v16))
            vList = botVertsDofDs[str(xNum) + "," + str(yNum)]["y+"] + botVertsDofDs[str(xNum) + "," + str(yNum)]["++"] + botVertsDofDs[str(xNum) + "," + str(yNum)]["x+"]
            for i in range(1, len(vList)):
                bme.faces.new((vList[i], vList[i-1], v13))
            vList = botVertsDofDs[str(0) + "," + str(yNum)]["x-"] + botVertsDofDs[str(0) + "," + str(yNum)]["-+"] + botVertsDofDs[str(0) + "," + str(yNum)]["y+"]
            for i in range(1, len(vList)):
                bme.faces.new((vList[i], vList[i-1], v14))

            # Make edge faces
            v = botVertsDofDs[str(xNum) + "," + str(yNum)]["y+"][0]
            bme.faces.new((v14, v13, v))
            v = botVertsDofDs[str(0) + "," + str(yNum)]["x-"][0]
            bme.faces.new((v15, v14, v))
            v = botVertsDofDs[str(0) + "," + str(0)]["y-"][0]
            bme.faces.new((v16, v15, v))
            v = botVertsDofDs[str(xNum) + "," + str(0)]["x+"][0]
            bme.faces.new((v13, v16, v))
            for xNum in range(1, brickSize[0]):
                v1 = botVertsDofDs[str(xNum) + "," + str(yNum)]["y+"][0]
                v2 = botVertsDofDs[str(xNum-1) + "," + str(yNum)]["y+"][0]
                bme.faces.new((v1, v2, v14))
                v1 = botVertsDofDs[str(xNum) + "," + str(0)]["y-"][0]
                v2 = botVertsDofDs[str(xNum-1) + "," + str(0)]["y-"][0]
                bme.faces.new((v16, v2, v1))
            for yNum in range(1, brickSize[1]):
                v1 = botVertsDofDs[str(xNum) + "," + str(yNum)]["x+"][0]
                v2 = botVertsDofDs[str(xNum) + "," + str(yNum-1)]["x+"][0]
                bme.faces.new((v13, v2, v1))
                v1 = botVertsDofDs[str(0) + "," + str(yNum)]["x-"][0]
                v2 = botVertsDofDs[str(0) + "," + str(yNum-1)]["x-"][0]
                bme.faces.new((v1, v2, v15))

            # Make in-between-insets faces along x axis
            for xNum in range(1, brickSize[0]):
                for yNum in range(brickSize[1]):
                    vList1 = botVertsDofDs[str(xNum-1) + "," + str(yNum)]["y+"] + botVertsDofDs[str(xNum-1) + "," + str(yNum)]["++"] + botVertsDofDs[str(xNum-1) + "," + str(yNum)]["x+"] + botVertsDofDs[str(xNum-1) + "," + str(yNum)]["+-"] + botVertsDofDs[str(xNum-1) + "," + str(yNum)]["y-"]
                    vList2 = botVertsDofDs[str(xNum) + "," + str(yNum)]["y+"] + botVertsDofDs[str(xNum) + "," + str(yNum)]["-+"][::-1] + botVertsDofDs[str(xNum) + "," + str(yNum)]["x-"] + botVertsDofDs[str(xNum) + "," + str(yNum)]["--"][::-1] + botVertsDofDs[str(xNum) + "," + str(yNum)]["y-"]
                    for i in range(1, len(vList1)):
                        v1 = vList1[i]
                        v2 = vList1[i-1]
                        v3 = vList2[i-1]
                        v4 = vList2[i]
                        bme.faces.new((v1, v2, v3, v4))

            # Make in-between-inset quads
            for yNum in range(1, brickSize[1]):
                for xNum in range(1, brickSize[0]):
                    v1 = botVertsDofDs[str(xNum-1) + "," + str(yNum)]["y-"][0]
                    v2 = botVertsDofDs[str(xNum) + "," + str(yNum)]["y-"][0]
                    v3 = botVertsDofDs[str(xNum) + "," + str(yNum-1)]["y+"][0]
                    v4 = botVertsDofDs[str(xNum-1) + "," + str(yNum-1)]["y+"][0]
                    bme.faces.new((v1, v2, v3, v4))

            # Make final in-between-insets faces on extremes of x axis along y axis
            for yNum in range(1, brickSize[1]):
                vList1 = botVertsDofDs[str(0) + "," + str(yNum-1)]["x-"] + botVertsDofDs[str(0) + "," + str(yNum-1)]["-+"] + botVertsDofDs[str(0) + "," + str(yNum-1)]["y+"]
                vList2 = botVertsDofDs[str(0) + "," + str(yNum)]["x-"] + botVertsDofDs[str(0) + "," + str(yNum)]["--"][::-1] + botVertsDofDs[str(0) + "," + str(yNum)]["y-"]
                for i in range(1, len(vList1)):
                    v1 = vList1[i]
                    v2 = vList1[i-1]
                    v3 = vList2[i-1]
                    v4 = vList2[i]
                    bme.faces.new((v1, v2, v3, v4))
            for yNum in range(1, brickSize[1]):
                vList1 = botVertsDofDs[str(xNum) + "," + str(yNum-1)]["x+"] + botVertsDofDs[str(xNum) + "," + str(yNum-1)]["++"][::-1] + botVertsDofDs[str(xNum) + "," + str(yNum-1)]["y+"]
                vList2 = botVertsDofDs[str(xNum) + "," + str(yNum)]["x+"] + botVertsDofDs[str(xNum) + "," + str(yNum)]["+-"] + botVertsDofDs[str(xNum) + "," + str(yNum)]["y-"]
                for i in range(1, len(vList1)):
                    v1 = vList2[i]
                    v2 = vList2[i-1]
                    v3 = vList1[i-1]
                    v4 = vList1[i]
                    bme.faces.new((v1, v2, v3, v4))

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
