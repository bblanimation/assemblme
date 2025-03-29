"""
Copyright (C) 2017 Bricks Brought to Life
http://bricksbroughttolife.com/
chris@bricksbroughttolife.com

Created by Christopher Gearhart
"""

# Module imports
from .preferences import *
from .report_error import *
from .property_groups import *
from ..ui import *
from ..operators import *


classes = [
    # assemblme/operators
    create_build_animation.ASSEMBLME_OT_create_build_animation,
    info_restore_preset.ASSEMBLME_OT_info_restore_preset,
    new_group_from_selection.ASSEMBLME_OT_new_group_from_selection,
    presets.ASSEMBLME_OT_anim_presets,
    refresh_build_animation_length.ASSEMBLME_OT_refresh_anim_length,
    start_over.ASSEMBLME_OT_start_over,
    visualizer.ASSEMBLME_OT_visualizer,
    aglist_actions.AGLIST_OT_list_action,
    aglist_actions.AGLIST_OT_copy_settings_to_others,
    aglist_actions.AGLIST_OT_copy_settings,
    aglist_actions.AGLIST_OT_paste_settings,
    aglist_actions.AGLIST_OT_set_to_active,
    aglist_actions.AGLIST_OT_print_all_items,
    aglist_actions.AGLIST_OT_clear_all_items,
    # assemblme/ui
    ASSEMBLME_MT_copy_paste_menu,
    ASSEMBLME_PT_animations,
    ASSEMBLME_PT_actions,
    ASSEMBLME_PT_settings,
    ASSEMBLME_PT_visualizer_settings,
    ASSEMBLME_PT_preset_manager,
    ASSEMBLME_UL_items,
    # assemblme/lib
    ASSEMBLME_PT_preferences,
    SCENE_OT_report_error,
    SCENE_OT_close_report_error,
    AnimatedCollectionProperties,
    AssemblMeProperties,
]
