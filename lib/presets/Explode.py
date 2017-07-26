import bpy
def execute():
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    ag.buildSpeed = 1
    ag.objectVelocity = 15
    ag.xLocOffset = 0
    ag.yLocOffset = 0
    ag.zLocOffset = 0
    ag.locInterpolationMode = "LINEAR"
    ag.locationRandom = 20
    ag.xRotOffset = 0
    ag.yRotOffset = 0
    ag.zRotOffset = 0
    ag.rotInterpolationMode = "LINEAR"
    ag.rotationRandom = 20
    ag.xOrient = 0
    ag.yOrient = 0
    ag.orientRandom = 50
    ag.layerHeight = 15
    ag.buildType = "Disassemble"
    ag.invertBuild = False
    return None
