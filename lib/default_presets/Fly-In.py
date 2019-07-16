import bpy
def execute():
    scn = bpy.context.scene
    ag = scn.aglist[scn.aglist_index]
    ag.build_speed = 1.0
    ag.velocity = 3.0
    ag.loc_offset = (0, 0, 0)
    ag.loc_interpolation_mode = 'BEZIER'
    ag.loc_random = 20.0
    ag.rot_offset = (0, 0, 0)
    ag.rot_interpolation_mode = 'BEZIER'
    ag.rot_random = 20.0
    ag.orient = (0, 0)
    ag.orient_random = 50.0
    ag.layer_height = 0.1
    ag.build_type = 'ASSEMBLE'
    ag.inverted_build = 0
    ag.skip_empty_selections = False
    ag.use_global = False
    ag.mesh_only = False
    return None
