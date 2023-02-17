from .texture_custom import TMUnlimiterObjectTextureCustom
from .texture_props import (
    TMUnlimiterTextureProps,
    TMUnlimiterDiffuseProps,
    TMUnlimiterSpecularProps,
    TMUnlimiterNormalProps,
    TMUnlimiterLightingProps,
    TMUnlimiterOcclusionProps,
)
from .texture_game import TMUnlimiterObjectTextureGame
from ..blender_gbx import GbxArchive
import bpy

class TMUnlimiterObjectTextureProps( bpy.types.PropertyGroup ) :

    texture_type: bpy.props.EnumProperty(
        name = "Texture type",
        items = [
            ( "None", "No texture", "No texture" ),
            ( "Game", "Game texture", "Game provided texture" ),
            ( "Custom", "Custom texture", "User provided texture" ),
        ],
        default = "None",
    )

    texture_custom: bpy.props.PointerProperty(
        type = TMUnlimiterObjectTextureCustom,
    )

    texture_game: bpy.props.PointerProperty(
        type = TMUnlimiterObjectTextureGame,
    )

    def archive( self, gbx: GbxArchive ) :
        if self.texture_props.texture_type == "None" :
            gbx.nat32( 0xffffffff )
        else :
            self.texture_props.archive( gbx )

def __register__() :
    bpy.utils.register_class( TMUnlimiterTextureProps )
    bpy.utils.register_class( TMUnlimiterDiffuseProps )
    bpy.utils.register_class( TMUnlimiterSpecularProps )
    bpy.utils.register_class( TMUnlimiterNormalProps )
    bpy.utils.register_class( TMUnlimiterLightingProps )
    bpy.utils.register_class( TMUnlimiterOcclusionProps )
    bpy.utils.register_class( TMUnlimiterObjectTextureCustom )
    bpy.utils.register_class( TMUnlimiterObjectTextureGame )
    bpy.utils.register_class( TMUnlimiterObjectTextureProps )

def __unregister__() :
    bpy.utils.unregister_class( TMUnlimiterObjectTextureProps )
    bpy.utils.unregister_class( TMUnlimiterObjectTextureGame )
    bpy.utils.unregister_class( TMUnlimiterObjectTextureCustom )
    bpy.utils.unregister_class( TMUnlimiterOcclusionProps )
    bpy.utils.unregister_class( TMUnlimiterLightingProps )
    bpy.utils.unregister_class( TMUnlimiterNormalProps )
    bpy.utils.unregister_class( TMUnlimiterSpecularProps )
    bpy.utils.unregister_class( TMUnlimiterDiffuseProps )
    bpy.utils.unregister_class( TMUnlimiterTextureProps )