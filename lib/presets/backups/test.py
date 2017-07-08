import bpy
def execute():
    scn = bpy.context.scene
    scn.buildSpeed = 1.0
    scn.objectVelocity = 30.0
    scn.xLocOffset = 0.0
    scn.yLocOffset = 0.0
    scn.zLocOffset = 20.0
    scn.locInterpolationMode = 'CUBIC'
    scn.locationRandom = 0.0
    scn.xRotOffset = 0.0
    scn.yRotOffset = 0.0
    scn.zRotOffset = 0.0
    scn.rotInterpolationMode = 'LINEAR'
    scn.rotationRandom = 0.0
    scn.xOrient = 0.0
    scn.yOrient = 0.0
    scn.orientRandom = 0.0010000000474974513
    scn.layerHeight = 0.009999999776482582
    scn.buildType = 'Assemble'
    scn.invertBuild = False
    return None