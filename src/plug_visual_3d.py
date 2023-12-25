from .blender_gbx import GbxArchive
import bmesh
import math
import bpy

def plug_visual_3d( gbx: GbxArchive, object: bpy.types.Object ) :
    mesh = bmesh.new()
    mesh.from_object( object, gbx.context[ "depsgraph" ] )
    bmesh.ops.triangulate( mesh, faces = mesh.faces )

    uvs = list( enumerate( mesh.loops.layers.uv.values() ) )
    tris = mesh.calc_loop_triangles()

    loops = []
    verts_data = {}
    min_vert_coord = [ +math.inf, +math.inf, +math.inf ]
    max_vert_coord = [ -math.inf, -math.inf, -math.inf ]

    for tri_loops in tris :
        for tri_loop in tri_loops :
            vert = tri_loop.vert
            uv_code = []

            for uv_idx, uv_layer in uvs :
                uv_code.append( tri_loop[ uv_layer ].uv.to_tuple() )

            if vert.index not in verts_data :
                verts, uv_codes = verts_data[ vert.index ] = (
                    [ vert ],    # verts
                    [ uv_code ], # uv_codes
                )
            else :
                verts, uv_codes = verts_data[ vert.index ]

            if uv_code not in uv_codes :
                new_vert = mesh.verts.new( vert.co, vert )
                new_vert.index = len( mesh.verts ) - 1
                verts.append( new_vert )

                verts_data[ new_vert.index ] = verts_data[ vert.index ]
                uv_codes.append( uv_code )
                vert = new_vert
            else :
                vert = verts[ uv_codes.index( uv_code ) ]

            min_vert_coord[ 0 ] = min( min_vert_coord[ 0 ], vert.co.x )
            min_vert_coord[ 1 ] = min( min_vert_coord[ 1 ], vert.co.y )
            min_vert_coord[ 2 ] = min( min_vert_coord[ 2 ], vert.co.z )
            max_vert_coord[ 0 ] = max( max_vert_coord[ 0 ], vert.co.x )
            max_vert_coord[ 1 ] = max( max_vert_coord[ 1 ], vert.co.y )
            max_vert_coord[ 2 ] = max( max_vert_coord[ 2 ], vert.co.z )

            loops.append( vert.index )

    if len( mesh.verts ) > 65535 :
        raise Exception( f'Object "{ object.name }" exceeds 65535 vertices' )

# 09-01E-000 -- Start
    gbx.nat32( 0x0901E000 )
# 09-006-00E -- Start
    gbx.nat32( 0x0900600E )
    gbx.nat32( 0x00000078 )
    gbx.nat32( len( uvs ) )
    gbx.nat32( len( mesh.verts ) )
    gbx.nat32( 0x00000000 )

    mesh.verts.ensure_lookup_table()

    for uv_idx, _ in uvs :
        gbx.nat32( 0x00000000 )

        for vert in mesh.verts :
            if vert.index in verts_data :
                verts, uv_codes = verts_data[ vert.index ]
                uv_coord = uv_codes[ verts.index( vert ) ][ uv_idx ]

                gbx.real( uv_coord[ 0 ] )
                gbx.real( uv_coord[ 1 ] )
            else :
                gbx.real( 0 )
                gbx.real( 0 )

    half_diag = (
        ( max_vert_coord[ 0 ] - min_vert_coord[ 0 ] ) / 2,
        ( max_vert_coord[ 1 ] - min_vert_coord[ 1 ] ) / 2,
        ( max_vert_coord[ 2 ] - min_vert_coord[ 2 ] ) / 2,
    )

    gbx.real( min_vert_coord[ 0 ] + half_diag[ 0 ] )
    gbx.real( min_vert_coord[ 1 ] + half_diag[ 1 ] )
    gbx.real( min_vert_coord[ 2 ] + half_diag[ 2 ] )
    gbx.real( half_diag[ 0 ] )
    gbx.real( half_diag[ 1 ] )
    gbx.real( half_diag[ 2 ] )
    gbx.nat32( 0x00000000 )
# 09-006-00E -- End
# 09-02C-004 -- Start
    gbx.nat32( 0x0902C004 )

    for vert in mesh.verts :
        gbx.real( vert.co.x )
        gbx.real( vert.co.z )
        gbx.real( -vert.co.y )
        gbx.real( vert.normal.x )
        gbx.real( vert.normal.z )
        gbx.real( -vert.normal.y )

        gbx.real( object.color[ 0 ] )
        gbx.real( object.color[ 1 ] )
        gbx.real( object.color[ 2 ] )
        gbx.real( object.color[ 3 ] )

    gbx.nat32( 0x00000000 )
    gbx.nat32( 0x00000000 )
# 09-02C-004 -- End
# 09-06A-001 -- Start
    gbx.nat32( 0x0906A001 )
    gbx.nat32( 0x00000001 )
# 09-057-000 -- Start
    gbx.nat32( 0x09057000 )
    gbx.nat32( 0x00000002 )
    gbx.nat32( len( loops ) )

    for loop in loops :
        gbx.nat16( loop )

    gbx.nat32( 0xFACADE01 )
# 09-057-000 -- End
# 09-06A-001 -- End
    gbx.nat32( 0xFACADE01 )
# 09-01E-000 -- End