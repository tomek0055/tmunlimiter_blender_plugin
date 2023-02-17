from .texture_props import (
    TMUnlimiterTextureProps,
    TMUnlimiterDiffuseProps,
    TMUnlimiterSpecularProps,
    TMUnlimiterNormalProps,
    TMUnlimiterLightingProps,
    TMUnlimiterOcclusionProps,
)
from ..blender_gbx import GbxArchive, ExternalRef
from pathlib import PureWindowsPath
import bpy

class TMUnlimiterObjectTextureCustom( bpy.types.PropertyGroup ) :

    usage: bpy.props.EnumProperty(
        name = "Texture usage",
        items = [
            ( "0", "Use diffuse", "Use diffuse" ),
            ( "1", "Use diffuse, specular", "Use diffuse and specular" ),
            ( "2", "Use diffuse, specular and normal", "Use diffuse, specular and normal" ),
            ( "3", "Use diffuse, specular, normal, lighting and occlusion", "Use diffuse, specular, normal, lighting and occlusion" ),
        ],
        default = "0",
    )

    is_double_sided: bpy.props.BoolProperty(
        name = "Is double sided",
        default = False,
    )

    diffuse: bpy.props.PointerProperty(
        name = "Diffuse texture",
        type = TMUnlimiterDiffuseProps
    )

    specular: bpy.props.PointerProperty(
        name = "Specular texture",
        type = TMUnlimiterSpecularProps
    )

    normal: bpy.props.PointerProperty(
        name = "Normal texture",
        type = TMUnlimiterNormalProps
    )

    lighting: bpy.props.PointerProperty(
        name = "Lighting texture",
        type = TMUnlimiterLightingProps
    )

    occlusion: bpy.props.PointerProperty(
        name = "Occlusion texture",
        type = TMUnlimiterOcclusionProps
    )

    def archive( self, gbx: GbxArchive ) :
        def get_replacement_texture_instance_index( replacement_texture_type: int ) -> int :
            replacement_textures = gbx.context[ "replacement_textures" ]

            if replacement_texture_type not in replacement_textures :
                replacement_textures[ replacement_texture_type ] = gbx.add_instance( write = False )

            return replacement_textures[ replacement_texture_type ]

        def get_or_create_texture_instance_index( texture: TMUnlimiterTextureProps ) -> int :
            texture_filepath = PureWindowsPath( texture.filepath )

            if not texture_filepath.name :
                raise Exception(
                    "Provided file path \"{0}\" for {1} texture does not have any file name".format( texture.filepath, texture.get_texture_type().lower() )
                )

            custom_texture_references = gbx.context[ "custom_texture_references" ]

            custom_texture_tuple = (
                str( texture_filepath ), texture.filtering, texture.addressing
            )

            if custom_texture_tuple not in custom_texture_references :
                custom_texture_references[ custom_texture_tuple ] = gbx.add_instance( write = False )

            return custom_texture_references[ custom_texture_tuple ]

        def plug_material_custom( gbx: GbxArchive ) :
            gbx.nat32( 0x0903a000 )
            gbx.nat32( 0x0903a006 )

            if self.usage == "0" :
                textures = [
                    ( "Diffuse", get_or_create_texture_instance_index( self.diffuse ) ),
                    ( "Specular", get_replacement_texture_instance_index( 2 ) ),
                    ( "Normal", get_replacement_texture_instance_index( 3 ) ),
                    ( "Occlusion", get_replacement_texture_instance_index( 0 ) ),
                    ( "Lighting", get_replacement_texture_instance_index( 1 ) ),
                ]
            elif self.usage == "1" :
                textures = [
                    ( "Diffuse", get_or_create_texture_instance_index( self.diffuse ) ),
                    ( "Specular", get_or_create_texture_instance_index( self.specular ) ),
                    ( "Normal", get_replacement_texture_instance_index( 3 ) ),
                    ( "Occlusion", get_replacement_texture_instance_index( 0 ) ),
                    ( "Lighting", get_replacement_texture_instance_index( 1 ) ),
                ]
            elif self.usage == "2" :
                textures = [
                    ( "Diffuse", get_or_create_texture_instance_index( self.diffuse ) ),
                    ( "Specular", get_or_create_texture_instance_index( self.specular ) ),
                    ( "Normal", get_or_create_texture_instance_index( self.normal ) ),
                    ( "Occlusion", get_replacement_texture_instance_index( 0 ) ),
                    ( "Lighting", get_replacement_texture_instance_index( 1 ) ),
                ]
            elif self.usage == "3" :
                textures = [
                    ( "Diffuse", get_or_create_texture_instance_index( self.diffuse ) ),
                    ( "Specular", get_or_create_texture_instance_index( self.specular ) ),
                    ( "Normal", get_or_create_texture_instance_index( self.normal ) ),
                    ( "Occlusion", get_or_create_texture_instance_index( self.occlusion ) ),
                    ( "Lighting", get_or_create_texture_instance_index( self.lighting ) ),
                ]
            else :
                raise Exception( "Unknown texture usage \"{0}\"".format( self.usage ) )

            gbx.nat32( len( textures ) )
            for texture_type, texture_instance_index in textures :
                gbx.mw_id( texture_type )
                gbx.nat32( 0 )
                gbx.nat32( texture_instance_index )

            gbx.nat32( 0x0903a00c )
            gbx.nat32( 3 )
            gbx.mw_id( "PreLightGen" )
            gbx.nat32( 0 )
            gbx.mw_id( "Normal" )
            gbx.nat32( 0 )
            gbx.mw_id( "Lighting" )
            gbx.nat32( 0 )

            gbx.nat32( 0x0903a00d )
            shader_requirements = 0
            custom_material_flags = 0

            if self.is_double_sided :
                shader_requirements = 1024
                custom_material_flags = 4

            gbx.nat64( custom_material_flags )
            gbx.nat64( shader_requirements )
            gbx.nat32( 0xfacade01 )

        def plug_material( gbx: GbxArchive ) :
            gbx.nat32( 0x09079000 )
            gbx.nat32( 0x09079007 )
            gbx.mw_ref( plug_material_custom )
            gbx.nat32( 0x0907900d )
            gbx.external_ref( ( "Techno2", "Media", "Material" ), ExternalRef( "TDiff_Spec_Nrm TOcc CSpecSoft.Material.Gbx" ) )
            gbx.nat32( 0xfacade01 )

        gbx.mw_ref( plug_material )