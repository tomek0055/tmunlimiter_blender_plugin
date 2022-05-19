from .texture_custom import TMUnlimiterObjectTextureCustom
from .texture_game import TMUnlimiterObjectTextureGame
import bpy

class TMUnlimiterObjectTextureProps( bpy.types.PropertyGroup ) :

    texture_type : bpy.props.EnumProperty(
        name = "Texture type",
        items = [
            ( "None", "No texture", "No texture" ),
            ( "Game", "Game texture", "Game provided texture" ),
            ( "Custom", "Custom texture", "User provided texture" ),
        ],
        default = "None",
    )

    texture_custom : bpy.props.PointerProperty(
        type = TMUnlimiterObjectTextureCustom,
    )

    texture_game : bpy.props.PointerProperty(
        type = TMUnlimiterObjectTextureGame,
    )

def __register__() :
    bpy.utils.register_class( TMUnlimiterObjectTextureCustom )
    bpy.utils.register_class( TMUnlimiterObjectTextureGame )
    bpy.utils.register_class( TMUnlimiterObjectTextureProps )

def __unregister__() :
    bpy.utils.unregister_class( TMUnlimiterObjectTextureProps )
    bpy.utils.unregister_class( TMUnlimiterObjectTextureGame )
    bpy.utils.unregister_class( TMUnlimiterObjectTextureCustom )