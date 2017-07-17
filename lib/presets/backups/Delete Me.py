import bpy
def execute():
    scn = bpy.context.scene
    scn.buildSpeed = 5.0
    scn.objectVelocity = 15.0
    scn.xLocOffset = 0.0
    scn.yLocOffset = 0.0
    scn.zLocOffset = 3.0
    scn.locInterpolationMode = 'CONSTANT'
    scn.locationRandom = 0.0
    scn.xRotOffset = 0.0
    scn.yRotOffset = 0.0
    scn.zRotOffset = 0.0
    scn.rotInterpolationMode = 'CONSTANT'
    scn.rotationRandom = 0.0
    scn.xOrient = 0.0
    scn.yOrient = 0.0
    scn.orientRandom = 0.20000000298023224
    scn.layerHeight = 0.0010000000474974513
    scn.buildType = 'Assemble'
    scn.invertBuild = False
    return None