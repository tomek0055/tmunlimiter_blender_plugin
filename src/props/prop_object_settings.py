
from ..object_texture.object_texture_props import (
    TMUnlimiterObjectTextureProps,
    __register__ as object_texture_props_register,
    __unregister__ as object_texture_props_unregister,
)

import bpy

class TMUnlimiterObjectSettingsProps( bpy.types.PropertyGroup ) :

    object_usage : bpy.props.EnumProperty(
        name = "Object usage",
        items = [
            ( "Model", "Model", "Model" ),
            ( "Trigger", "Trigger", "Trigger" ),
        ],
        default = "Model",
    )

    texture_props : bpy.props.PointerProperty(
        type = TMUnlimiterObjectTextureProps,
    )

class TMUnlimiterObjectSettings( bpy.types.Panel ) :
    bl_idname = "UNLIMITER_PT_object_settings"
    bl_label = "TMUnlimiter - Object settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw_model_ui( self, props : TMUnlimiterObjectTextureProps ) :
        self.layout.prop( props, "texture_type" )

        if props.texture_type == "Custom" :
            layout = self.layout.box()

            layout.prop( props.texture_custom, "type" )
            layout.prop( props.texture_custom, "diffuse_filepath" )

            if props.texture_custom.type == "1" :
                layout.prop( props.texture_custom, "specular_filepath" )
                layout.prop( props.texture_custom, "normal_filepath" )
            
            layout.prop( props.texture_custom, "is_translucent" )
            layout.prop( props.texture_custom, "is_double_sided" )
            layout.prop( props.texture_custom, "texture_filter" )
            layout.prop( props.texture_custom, "texture_address" )

        elif props.texture_type == "Game" :
            layout = self.layout.box()

            layout.prop( props.texture_game, "environment" )
            layout.prop( props.texture_game, "game_material" )

    def draw( self, context : bpy.context ) :
        data : TMUnlimiterObjectSettingsProps = context.active_object.unlimiter_object_settings

        self.layout.prop( data, "object_usage" )

        if data.object_usage == "Model" :
            self.draw_model_ui( data.texture_props )

def __register__() :
    object_texture_props_register()

    bpy.utils.register_class( TMUnlimiterObjectSettingsProps )
    bpy.utils.register_class( TMUnlimiterObjectSettings )

    bpy.types.Object.unlimiter_object_settings = bpy.props.PointerProperty(
        type = TMUnlimiterObjectSettingsProps
    )

def __unregister__() :
    bpy.utils.unregister_class( TMUnlimiterObjectSettings )
    bpy.utils.unregister_class( TMUnlimiterObjectSettingsProps )

    object_texture_props_unregister()