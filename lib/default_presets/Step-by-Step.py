import bpy
def execute():
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    ag.build_speed = 40.0
    ag.velocity = 10.0
    ag.loc_offset = (0, 0, 25)
    ag.loc_interpolation_mode = "CONSTANT"
    ag.loc_random = 0.0
    ag.rot_offset = (0, 0, 0)
    ag.rot_interpolation_mode = "LINEAR"
    ag.rot_random = 0.0
    ag.orient = (0, 0)
    ag.orient_random = 0.001
    ag.layer_height = 0.005
    ag.build_type = "ASSEMBLE"
    ag.inverted_build = False
    ag.skip_empty_selections = True
    ag.use_global = True
    ag.mesh_only = True
    return None
