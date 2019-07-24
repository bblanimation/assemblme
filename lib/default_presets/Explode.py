import bpy
def execute():
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    ag.build_speed = 1.0
    ag.velocity = 4.5
    ag.loc_offset = (0, 0, 0)
    ag.loc_interpolation_mode = "LINEAR"
    ag.loc_random = 20.0
    ag.rot_offset = (0, 0, 0)
    ag.rot_interpolation_mode = "LINEAR"
    ag.rot_random = 20.0
    ag.orient = (0, 0)
    ag.orient_random = 50.0
    ag.layer_height = 1000.0
    ag.build_type = "DISASSEMBLE"
    ag.inverted_build = False
    ag.skip_empty_selections = True
    ag.use_global = True
    ag.mesh_only = False
    return None
