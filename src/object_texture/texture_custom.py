from .texture_props import (
    TMUnlimiterTextureProps,
    TMUnlimiterDiffuseProps,
    TMUnlimiterSpecularProps,
    TMUnlimiterNormalProps,
    TMUnlimiterLightingProps,
    TMUnlimiterOcclusionProps,
    TMUnlimiterCubeAmbientProps,
    TMUnlimiterReflectSoftProps,
    TMUnlimiterFresnelProps,
    TMUnlimiterCloudsProps,
)
from ..blender_gbx import GbxArchive, ExternalRef
from pathlib import PureWindowsPath
import bpy

class TMUnlimiterObjectTextureCustom( bpy.types.PropertyGroup ) :
    use_diffuse: bpy.props.BoolProperty(
        name = "Use diffuse",
        default = True
    )

    use_specular: bpy.props.BoolProperty(
        name = "Use specular"
    )

    use_normal: bpy.props.BoolProperty(
        name = "Use normal"
    )

    use_lighting: bpy.props.BoolProperty(
        name = "Use lighting"
    )

    use_occlusion: bpy.props.BoolProperty(
        name = "Use occlusion"
    )

    override_cube_ambient: bpy.props.BoolProperty(
        name = "Override cube ambient"
    )

    override_reflect_soft: bpy.props.BoolProperty(
        name = "Override reflect soft"
    )

    override_fresnel: bpy.props.BoolProperty(
        name = "Override fresnel"
    )

    override_clouds: bpy.props.BoolProperty(
        name = "Override clouds"
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

    cube_ambient: bpy.props.PointerProperty(
        name = "Cube ambient",
        type = TMUnlimiterCubeAmbientProps
    )

    reflect_soft: bpy.props.PointerProperty(
        name = "Reflect soft",
        type = TMUnlimiterReflectSoftProps
    )

    fresnel: bpy.props.PointerProperty(
        name = "Fresnel",
        type = TMUnlimiterFresnelProps
    )

    clouds: bpy.props.PointerProperty(
        name = "Clouds",
        type = TMUnlimiterCloudsProps
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
                raise Exception( f'Provided file path "{ texture.filepath }" for { texture.get_texture_type().lower() } texture does not have any file name' )

            custom_texture_references = gbx.context[ "custom_texture_references" ]

            custom_texture_tuple = (
                str( texture_filepath ), texture.filtering, texture.addressing
            )

            if custom_texture_tuple not in custom_texture_references :
                custom_texture_references[ custom_texture_tuple ] = gbx.add_instance( write = False )

            return custom_texture_references[ custom_texture_tuple ]

        def plug_material_custom( gbx: GbxArchive ) :
            textures = []

            gbx.nat32( 0x0903a000 )
            gbx.nat32( 0x0903a006 )

            if self.use_diffuse:
                textures.append( ( "Diffuse", get_or_create_texture_instance_index( self.diffuse ) ) )
            else:
                textures.append( ( "Diffuse", get_replacement_texture_instance_index( 0 ) ) )
            
            if self.use_specular:
                textures.append( ( "Specular", get_or_create_texture_instance_index( self.specular ) ) )
            else:
                textures.append( ( "Specular", get_replacement_texture_instance_index( 2 ) ) )

            if self.use_normal:
                textures.append( ( "Normal", get_or_create_texture_instance_index( self.normal ) ) )
            else:
                textures.append( ( "Normal", get_replacement_texture_instance_index( 3 ) ) )

            if self.use_lighting:
                textures.append( ( "Lighting", get_or_create_texture_instance_index( self.lighting ) ) )
            else:
                textures.append( ( "Lighting", get_replacement_texture_instance_index( 1 ) ) )

            if self.use_occlusion:
                textures.append( ( "Occlusion", get_or_create_texture_instance_index( self.occlusion ) ) )
            else:
                textures.append( ( "Occlusion", get_replacement_texture_instance_index( 0 ) ) )

            if self.override_cube_ambient:
                textures.append( ( "CubeAmbient", get_or_create_texture_instance_index( self.cube_ambient ) ) )
            
            if self.override_reflect_soft:
                textures.append( ( "ReflectSoft", get_or_create_texture_instance_index( self.reflect_soft ) ) )

            if self.override_fresnel:
                textures.append( ( "Fresnel", get_or_create_texture_instance_index( self.fresnel ) ) )

            if self.override_clouds:
                textures.append( ( "Clouds", get_or_create_texture_instance_index( self.clouds ) ) )

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