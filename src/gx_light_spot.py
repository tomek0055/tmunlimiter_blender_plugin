from .blender_gbx import BlenderGbx

from math import (
    pi,
    cos,
    sin,
    sqrt,
    atan2,
    degrees,
)

import bpy

def gx_light_spot( gbx : BlenderGbx, light : bpy.types.SpotLight ) :
    gbx.nat32( 0x0400B000 )

    gbx.nat32( 0x04001001 )
    gbx.real( light.color[ 0 ] )
    gbx.real( light.color[ 1 ] )
    gbx.real( light.color[ 2 ] )
    gbx.real( light.energy / 200 )
    gbx.nat32( 1 )
    gbx.nat32( 1 )

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

    gbx.nat32( 0x0400B000 )
    gbx.real( outer_angle )
    gbx.real( inner_angle )
    gbx.real( light.spot_blend )

    gbx.nat32( 0xFACADE01 )