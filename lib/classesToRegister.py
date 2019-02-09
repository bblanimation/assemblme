"""
Copyright (C) 2017 Bricks Brought to Life
http://bblanimation.com/
chris@bblanimation.com

Created by Christopher Gearhart
"""

# updater import
from . import addon_updater_ops
from .ui import *
from .buttons import *
from .buttons.presets import *
from .functions import getPresetTuples
from .preferences import *
from .reportError import *


classes = [
    # assemblme/buttons
    buttons.createBuildAnimation.ASSEMBLME_OT_create_build_animation,
    buttons.infoRestorePreset.ASSEMBLME_OT_info_restore_preset,
    buttons.newCollection.ASSEMBLME_OT_new_collection_from_selection,
    buttons.presets.ASSEMBLME_OT_anim_presets,
    buttons.refreshBuildAnimationLength.ASSEMBLME_OT_refresh_anim_length,
    buttons.startOver.ASSEMBLME_OT_start_over,
    buttons.visualizer.ASSEMBLME_OT_visualizer,
    # assemblme/ui/aglist_attrs
    ASSEMBLME_UL_animated_collections,
    # assemblme/ui/aglist_actions
    ASSEMBLME_OT_uilist_actions,
    ASSEMBLME_UL_uilist_items,
    ASSEMBLME_OT_uilist_copy_settings_to_others,
    ASSEMBLME_OT_uilist_copy_settings,
    ASSEMBLME_OT_uilist_paste_settings,
    ASSEMBLME_OT_uilist_print_all_items,
    ASSEMBLME_OT_uilist_set_source_coll_to_active,
    ASSEMBLME_OT_uilist_clear_all_items,
    # assemblme/ui
    ASSEMBLME_MT_basic_menu,
    ASSEMBLME_PT_animations,
    ASSEMBLME_PT_actions,
    ASSEMBLME_PT_settings,
    ASSEMBLME_PT_interface,
    ASSEMBLME_PT_preset_manager,
    # assemblme/lib
    ASSEMBLME_PT_preferences,
    SCENE_OT_report_error,
    SCENE_OT_close_report_error,
]
