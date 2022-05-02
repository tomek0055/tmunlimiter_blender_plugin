from .gbx import Gbx
import bpy

def plug_surface_geom( gbx : Gbx, object : bpy.types.Object ) :
    gbx.nat32( 0x0900F000 )
    gbx.nat32( 0x0900F004 )
    gbx.mw_id()
    # verts
    # faces
    # zero list
    # naura
    gbx.nat32( 0xFACADE01 )

def plug_surface( gbx : Gbx, object : bpy.types.Object ) :
    gbx.nat32( 0x0900C000 )
    gbx.nat32( 0x0900C000 )
    gbx.mw_ref( plug_surface_geom, object )
    gbx.nat32( 1 ) # num materials
    gbx.nat32( 0 ) # is internal mat
    gbx.nat16( 0 ) # internal mat idx
    gbx.nat32( 0xFACADE01 )