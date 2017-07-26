import bpy
def execute():
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    ag.buildSpeed = 1
    ag.objectVelocity = 25
    ag.xLocOffset = 0
    ag.yLocOffset = 0
    ag.zLocOffset = 5
    ag.locInterpolationMode = "CUBIC"
    ag.locationRandom = 0
    ag.xRotOffset = 0
    ag.yRotOffset = 0
    ag.zRotOffset = 0
    ag.rotInterpolationMode = "LINEAR"
    ag.rotationRandom = 0
    ag.xOrient = 0
    ag.yOrient = 0
    ag.orientRandom = 0.001
    ag.layerHeight = 0.01
    ag.buildType = "Assemble"
    ag.invertBuild = False
    return None
