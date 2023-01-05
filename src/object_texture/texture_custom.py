from ..blender_gbx import GbxArchive
from pathlib import PureWindowsPath
import bpy

class TMUnlimiterObjectTextureCustom( bpy.types.PropertyGroup ) :

    usage: bpy.props.EnumProperty(
        name = "Texture usage",
        items = [
            ( "0", "Use only diffuse", "Use only diffuse" ),
            ( "1", "Use diffuse, specular and normal", "Use diffuse, specular and normal" ),
        ],
        default = "0",
    )

    diffuse_filepath: bpy.props.StringProperty(
        name = "Diffuse texture file path",
        description = "Diffuse texture file path relative to the \"Texures\" directory",
    )

    specular_filepath: bpy.props.StringProperty(
        name = "Specular texture file path",
        description = "Specular texture file path relative to the \"Textures\" directory",
    )

    normal_filepath: bpy.props.StringProperty(
        name = "Normal texture file path",
        description = "Normal texture file path relative to the \"Textures\" directory",
    )

    is_translucent: bpy.props.BoolProperty(
        name = "Is translucent",
    )

    is_double_sided: bpy.props.BoolProperty(
        name = "Is double sided",
    )

    texture_filter: bpy.props.EnumProperty(
        name = "Texture filtering",
        items = [
            ( "Point", "Point", "Point" ),
            ( "Bilinear", "Bilinear", "Bilinear" ),
            ( "Trilinear", "Trilinear", "Trilinear" ),
            ( "Anisotropic", "Anisotropic", "Anisotropic" ),
        ],
        default = "Point",
    )

    texture_address: bpy.props.EnumProperty(
        name = "Texture addressing",
        items = [
            ( "Wrap", "Wrap", "Wrap" ),
            ( "Mirror", "Mirror", "Mirror" ),
            ( "Clamp", "Clamp", "Clamp" ),
            ( "BorderSM3", "BorderSM3", "BorderSM3" ),
        ],
        default = "Clamp",
    )

    def get_texture_refs( self, gbx: GbxArchive ) -> list[int] :
        custom_texture_refs: dict[str, tuple[int, str]] = gbx.context[ "custom_texture_refs" ]
        textures: list[int] = []

        if self.usage == "0" :
            texture_filepaths: list[str] = [
                self.diffuse_filepath,
            ]
        elif self.usage == "1" :
            texture_filepaths: list[str] = [
                self.diffuse_filepath,
                self.specular_filepath,
                self.normal_filepath,
            ]
        else :
            raise Exception( "Unknown texture usage \"{0}\"".format( self.usage ) )

        for texture_filepath in texture_filepaths :
            windows_path = PureWindowsPath( texture_filepath )

            if not windows_path.name :
                raise Exception( "File path does not have any file name" )

            texture_filepath = str( windows_path )

            if texture_filepath in custom_texture_refs :
                textures.append( custom_texture_refs[ texture_filepath ][ 0 ] )
            else :
                texture_instance_index = gbx.add_instance( write = False )

                custom_texture_refs[ texture_filepath ] = (
                    texture_instance_index,
                    texture_filepath
                )

                textures.append( texture_instance_index )

        return textures