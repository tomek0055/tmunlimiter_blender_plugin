from ..object_texture.object_texture_props import (
    TMUnlimiterObjectTextureProps,
    __register__ as object_texture_props_register,
    __unregister__ as object_texture_props_unregister,
)
from ..object_texture.texture_props import TMUnlimiterTextureProps
from ..blender_gbx import GbxArchive
import bpy

class TMUnlimiterObjectSettings( bpy.types.PropertyGroup ) :

    can_export_geometry: bpy.props.BoolProperty(
        name = "Export geometry",
        default = True,
        description = "This option controls export of the geometry data and textures",
    )

    can_export_collision: bpy.props.BoolProperty(
        name = "Export collision",
        default = False,
        description = "This option controls export of the collision data",
    )

    texture_props: bpy.props.PointerProperty(
        type = TMUnlimiterObjectTextureProps,
    )

    def archive_material( self, gbx: GbxArchive ) :
        if self.texture_props.texture_type == "Game" :
            self.texture_props.texture_game.archive( gbx )
        elif self.texture_props.texture_type == "Custom" :
            self.texture_props.texture_custom.archive( gbx )
        else :
            gbx.nat32( 0xffffffff )

class TMUnlimiterObjectSettingsPanel( bpy.types.Panel ) :
    bl_idname = "UNLIMITER_PT_object_settings"
    bl_label = "TMUnlimiter - Object settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw_model_ui( self, props: TMUnlimiterObjectTextureProps ) :
        self.layout.prop( props, "texture_type" )

        if props.texture_type == "Custom" :
            texture_custom = props.texture_custom

            layout_root = self.layout.box()
            layout_root.prop( texture_custom, "usage" )
            layout_root.prop( texture_custom, "is_double_sided" )

            def draw_texture_layout( layout, texture: TMUnlimiterTextureProps ) :
                texture_type = texture.get_texture_type()

                layout.prop( texture, "filepath", text = "{0} file path".format( texture_type ) )
                layout.prop( texture, "filtering", text = "{0} filtering".format( texture_type ) )
                layout.prop( texture, "addressing", text = "{0} addressing".format( texture_type ) )

            if props.texture_custom.usage == "0" :
                draw_texture_layout( layout_root.box(), texture_custom.diffuse )
            elif props.texture_custom.usage == "1" :
                draw_texture_layout( layout_root.box(), texture_custom.diffuse )
                draw_texture_layout( layout_root.box(), texture_custom.specular )
            elif props.texture_custom.usage == "2" :
                draw_texture_layout( layout_root.box(), texture_custom.diffuse )
                draw_texture_layout( layout_root.box(), texture_custom.specular )
                draw_texture_layout( layout_root.box(), texture_custom.normal )
            elif props.texture_custom.usage == "3" :
                draw_texture_layout( layout_root.box(), texture_custom.diffuse )
                draw_texture_layout( layout_root.box(), texture_custom.specular )
                draw_texture_layout( layout_root.box(), texture_custom.normal )
                draw_texture_layout( layout_root.box(), texture_custom.lighting )
                draw_texture_layout( layout_root.box(), texture_custom.occlusion )
        elif props.texture_type == "Game" :
            layout = self.layout.box()

            layout.prop( props.texture_game, "environment" )
            layout.prop( props.texture_game, "game_material" )

    def draw( self, context: bpy.context ) :
        data: TMUnlimiterObjectSettings = context.active_object.unlimiter_object_settings

        self.layout.prop( data, "can_export_geometry" )

        if data.can_export_geometry :
            self.draw_model_ui( data.texture_props )
        
        self.layout.prop( data, "can_export_collision" )

def __register__() :
    object_texture_props_register()

    bpy.utils.register_class( TMUnlimiterObjectSettings )
    bpy.utils.register_class( TMUnlimiterObjectSettingsPanel )

    bpy.types.Object.unlimiter_object_settings = bpy.props.PointerProperty(
        type = TMUnlimiterObjectSettings
    )

def __unregister__() :
    bpy.utils.unregister_class( TMUnlimiterObjectSettingsPanel )
    bpy.utils.unregister_class( TMUnlimiterObjectSettings )

    object_texture_props_unregister()