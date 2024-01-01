from __future__ import annotations

from math import ( pi, cos, sin,sqrt, atan2, degrees )
from ..blender_gbx import GbxArchive
import bpy

class TMUnlimiter_LightSettings( bpy.types.PropertyGroup ) :

    intensity: bpy.props.FloatProperty(
        min = 0.0,
        max = 1.0,
        default = 1.0,
        name = "Intensity",
    )

    specular_power: bpy.props.FloatProperty(
        default = 1.0,
        name = "Specular power",
    )

    shadow_intensity: bpy.props.FloatProperty(
        min = 0.0,
        max = 1.0,
        default = 1.0,
        name = "Shadow intensity",
    )

    flare_intensity: bpy.props.FloatProperty(
        min = 0.0,
        max = 1.0,
        default = 1.0,
        name = "Flare intensity",
    )

    shadow_color: bpy.props.FloatVectorProperty(
        min = 0.0,
        max = 1.0,
        name = "Shadow color",
        subtype = "COLOR",
    )

    point_flare_size: bpy.props.FloatProperty(
        name = "Flare size",
        default = 1.0,
    )

    ball_attenuation_1: bpy.props.FloatProperty(
        min = 0.0,
        max = 10.0,
        name = "Attenuation 1",
        default = 0.0,
    )

    ball_attenuation_2: bpy.props.FloatProperty(
        min = 0.0,
        max = 10.0,
        name = "Attenuation 2",
        default = 0.0,
    )

    ball_ambient_color: bpy.props.FloatVectorProperty(
        name = "Ambient color",
        subtype = "COLOR",
    )

    @staticmethod
    def archive( gbx: GbxArchive, light: bpy.types.PointLight | bpy.types.SpotLight ) :
        light_settings: TMUnlimiter_LightSettings = light.tmunlimiter_light_settings

        if light.type == "POINT" :
            gbx.nat32( 0x04_002_000 )
        elif light.type == "SPOT" :
            gbx.nat32( 0x04_00b_000 )
        else :
            raise Exception( f'Not supported light type "{ light.type }"' )

        gbx.nat32( 0x04001009 )
        gbx.real( light.color.r )
        gbx.real( light.color.g )
        gbx.real( light.color.b )
        gbx.nat32( 0x0000005d ) # flags
        gbx.real( light_settings.intensity )
        gbx.real( light.diffuse_factor )
        gbx.real( light.specular_factor )
        gbx.real( light_settings.specular_power )
        gbx.real( light_settings.shadow_intensity )
        gbx.real( light_settings.flare_intensity )
        gbx.real( light_settings.shadow_color.r )
        gbx.real( light_settings.shadow_color.g )
        gbx.real( light_settings.shadow_color.b )

        gbx.nat32( 0x04_003_004 )
        gbx.real( light_settings.point_flare_size )
        gbx.real( 0.0 )

        gbx.nat32( 0x04_002_006 )
        gbx.nat32( 0x00000000 ) # ball flags
        gbx.real( light.shadow_soft_size )
        gbx.real( light.shadow_soft_size )
        gbx.real( light.shadow_soft_size )
        gbx.real( light.shadow_soft_size )
        gbx.real( 0.0 )
        gbx.real( light_settings.ball_attenuation_1 )
        gbx.real( light_settings.ball_attenuation_2 )
        gbx.real( light_settings.ball_ambient_color.r )
        gbx.real( light_settings.ball_ambient_color.g )
        gbx.real( light_settings.ball_ambient_color.b )

        if light.type == "SPOT" :
            gbx.nat32( 0x04_00b_002 )
            gbx.nat32( 0x00000000 ) # spot flags

            cone_angle = light.spot_size
            inner_angle = outer_angle = degrees( cone_angle )

            if cone_angle < pi :
                cone_angle *= 0.5
                cone_angle_cos = cos( cone_angle )

                outer_cone_base = sin( cone_angle ) * 10
                outer_cone_height = cone_angle_cos * 10

                inner_cone_base = cone_angle_cos * light.spot_blend - cone_angle_cos - light.spot_blend

                inner_cone_base = outer_cone_base * sqrt( (
                    ( -cone_angle_cos - inner_cone_base * cone_angle_cos )
                    /
                    ( inner_cone_base - inner_cone_base * cone_angle_cos )
                ) )

                inner_angle = degrees(
                    atan2( inner_cone_base, outer_cone_height ) * 2
                )

            gbx.real( inner_angle )
            gbx.real( outer_angle )
            gbx.real( 0.0 )
            gbx.real( inner_angle )
            gbx.real( outer_angle )
            gbx.real( light.spot_blend )

        gbx.nat32( 0xfacade01 )

class TMUnlimiter_LightSettingsPanel( bpy.types.Panel ) :
    bl_idname = "UNLIMITER_PT_light_settings"
    bl_label = "TMUnlimiter - Light settings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll( self, context: bpy.context ) :
        return context.light and context.light.type in { "POINT", "SPOT" }

    def draw( self, context: bpy.context ) :
        light_settings: TMUnlimiter_LightSettings = context.light.tmunlimiter_light_settings

        self.layout.prop( light_settings, "intensity" )
        self.layout.prop( light_settings, "specular_power" )
        self.layout.prop( light_settings, "shadow_intensity" )
        self.layout.prop( light_settings, "flare_intensity" )
        self.layout.prop( light_settings, "shadow_color" )

        self.layout.separator()
        self.layout.prop( light_settings, "point_flare_size" )
        self.layout.prop( light_settings, "ball_attenuation_1" )
        self.layout.prop( light_settings, "ball_attenuation_2" )
        self.layout.prop( light_settings, "ball_ambient_color" )

def __register__() :
    bpy.utils.register_class( TMUnlimiter_LightSettings )
    bpy.utils.register_class( TMUnlimiter_LightSettingsPanel )

    bpy.types.Light.tmunlimiter_light_settings = bpy.props.PointerProperty( type = TMUnlimiter_LightSettings )

def __unregister__() :
    del bpy.types.Light.tmunlimiter_light_settings

    bpy.utils.unregister_class( TMUnlimiter_LightSettingsPanel )
    bpy.utils.unregister_class( TMUnlimiter_LightSettings )