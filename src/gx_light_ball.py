from .blender_gbx import BlenderGbx
from math import degrees
import bpy

def gx_light_ball( gbx : BlenderGbx, light : bpy.types.PointLight ) :
    gbx.nat32( 0x04002000 )

    gbx.nat32( 0x04001001 )
    gbx.real( light.color[ 0 ] )
    gbx.real( light.color[ 1 ] )
    gbx.real( light.color[ 2 ] )
    gbx.real( light.energy / 200 )
    gbx.nat32( 1 )
    gbx.nat32( 1 )

    gbx.nat32( 0x04002000 )
    gbx.real( light.shadow_soft_size )
    gbx.real( light.linear_attenuation )
    gbx.real( light.quadratic_attenuation )

    gbx.nat32( 0xFACADE01 )