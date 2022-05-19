import bpy

class TMUnlimiterObjectTextureCustom( bpy.types.PropertyGroup ) :

    type : bpy.props.EnumProperty(
        name = "Texture usage",
        items = [
            ( "0", "Use only diffuse", "Use only diffuse" ),
            ( "1", "Use diffuse, specular and normal", "Use diffuse, specular and normal" ),
        ],
        default = "0",
    )

    diffuse_filepath : bpy.props.StringProperty(
        name = "Diffuse texture file path",
        description = "Diffuse texture file path relative to the \"Texures\" directory",
    )

    specular_filepath : bpy.props.StringProperty(
        name = "Specular texture file path",
        description = "Specular texture file path relative to the \"Textures\" directory",
    )

    normal_filepath : bpy.props.StringProperty(
        name = "Normal texture file path",
        description = "Normal texture file path relative to the \"Textures\" directory",
    )

    is_translucent : bpy.props.BoolProperty(
        name = "Is translucent",
    )

    is_double_sided : bpy.props.BoolProperty(
        name = "Is double sided",
    )

    texture_filter : bpy.props.EnumProperty(
        name = "Texture filtering",
        items = [
            ( "Point", "Point", "Point" ),
            ( "Bilinear", "Bilinear", "Bilinear" ),
            ( "Trilinear", "Trilinear", "Trilinear" ),
            ( "Anisotropic", "Anisotropic", "Anisotropic" ),
        ],
        default = "Point",
    )

    texture_address : bpy.props.EnumProperty(
        name = "Texture addressing",
        items = [
            ( "Wrap", "Wrap", "Wrap" ),
            ( "Mirror", "Mirror", "Mirror" ),
            ( "Clamp", "Clamp", "Clamp" ),
            ( "BorderSM3", "BorderSM3", "BorderSM3" ),
        ],
        default = "Clamp",
    )