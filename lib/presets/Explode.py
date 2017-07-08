import bpy
def execute():
    scn = bpy.context.scene
    scn.buildSpeed = 1
    scn.objectVelocity = 15
    scn.xLocOffset = 0
    scn.yLocOffset = 0
    scn.zLocOffset = 0
    scn.locInterpolationMode = "LINEAR"
    scn.locationRandom = 20
    scn.xRotOffset = 0
    scn.yRotOffset = 0
    scn.zRotOffset = 0
    scn.rotInterpolationMode = "LINEAR"
    scn.rotationRandom = 20
    scn.xOrient = 0
    scn.yOrient = 0
    scn.orientRandom = 50
    scn.layerHeight = 15
    scn.buildType = "Disassemble"
    scn.invertBuild = False
    return None
