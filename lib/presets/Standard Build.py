import bpy
def execute():
    scn = bpy.context.scene
    scn.buildSpeed = 1
    scn.objectVelocity = 25
    scn.xLocOffset = 0
    scn.yLocOffset = 0
    scn.zLocOffset = 5
    scn.locInterpolationMode = "CUBIC"
    scn.locationRandom = 0
    scn.xRotOffset = 0
    scn.yRotOffset = 0
    scn.zRotOffset = 0
    scn.rotInterpolationMode = "LINEAR"
    scn.rotationRandom = 0
    scn.xOrient = 0
    scn.yOrient = 0
    scn.orientRandom = 0.001
    scn.layerHeight = 0.01
    scn.buildType = "Assemble"
    scn.invertBuild = False
    return None
