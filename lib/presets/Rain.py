import bpy
def execute():
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    ag.buildSpeed = 5.0
    ag.objectVelocity = 15.0
    ag.xLocOffset = 0.0
    ag.yLocOffset = 0.0
    ag.zLocOffset = 3.0
    ag.locInterpolationMode = 'BOUNCE'
    ag.locationRandom = 0.0
    ag.xRotOffset = 0.0
    ag.yRotOffset = 0.0
    ag.zRotOffset = 0.0
    ag.rotInterpolationMode = 'BACK'
    ag.rotationRandom = 0.0
    ag.xOrient = 0.0
    ag.yOrient = 0.0
    ag.orientRandom = 0.20000000298023224
    ag.layerHeight = 0.0010000000474974513
    ag.buildType = 'Assemble'
    ag.invertBuild = False
    return None
