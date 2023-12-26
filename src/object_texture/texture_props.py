from __future__ import annotations

import bpy

class TMUnlimiterTextureProps( bpy.types.PropertyGroup ) :

    filepath: bpy.props.StringProperty(
        name = "File path",
        description = "Texture file path relative to the \"Texures\" directory"
    )

    filtering: bpy.props.EnumProperty(
        name = "Texture filtering",
        items = [
            ( "0", "Point", "Point" ),
            ( "1", "Bilinear", "Bilinear" ),
            ( "2", "Trilinear", "Trilinear" ),
            ( "3", "Anisotropic", "Anisotropic" ),
        ],
        default = "3",
    )

    addressing: bpy.props.EnumProperty(
        name = "Texture addressing",
        items = [
            ( "0", "Wrap", "Wrap" ),
            ( "1", "Mirror", "Mirror" ),
            ( "2", "Clamp", "Clamp" ),
            ( "3", "BorderSM3", "BorderSM3" ),
        ],
        default = "2",
    )

    def copy_from( self, texture_props: TMUnlimiterTextureProps ) :
        self.filepath = texture_props.filepath
        self.filtering = texture_props.filtering
        self.addressing = texture_props.addressing

    def get_texture_type( self ) -> str :
        raise Exception( "Not implemented" )

class TMUnlimiterDiffuseProps( TMUnlimiterTextureProps ) :

    def get_texture_type( self ) -> str :
        return "Diffuse"

class TMUnlimiterSpecularProps( TMUnlimiterTextureProps ) :

    def get_texture_type( self ) -> str :
        return "Specular"

class TMUnlimiterNormalProps( TMUnlimiterTextureProps ) :

    def get_texture_type( self ) -> str :
        return "Normal"

class TMUnlimiterLightingProps( TMUnlimiterTextureProps ) :
    
    def get_texture_type(self) -> str :
        return "Lighting"

class TMUnlimiterOcclusionProps( TMUnlimiterTextureProps ) :

    def get_texture_type( self ) -> str :
        return "Occlusion"

class TMUnlimiterCubeAmbientProps( TMUnlimiterTextureProps ) :

    def get_texture_type( self ) -> str :
        return "Cube Ambient"

class TMUnlimiterReflectSoftProps( TMUnlimiterTextureProps ) :

    def get_texture_type( self ) -> str :
        return "Reflect Soft"

class TMUnlimiterFresnelProps( TMUnlimiterTextureProps ) :

    def get_texture_type( self ) -> str :
        return "Fresnel"

class TMUnlimiterCloudsProps( TMUnlimiterTextureProps ) :

    def get_texture_type( self ) -> str :
        return "Clouds"