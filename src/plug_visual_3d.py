from .blender_gbx import GbxArchive
import bmesh
import math
import bpy

def plug_visual_3d( gbx: GbxArchive, object: bpy.types.Object ) :
    mesh = bmesh.new()
    mesh.from_object( object, gbx.context[ "depsgraph" ] )

    if len( mesh.verts ) < 1 :
        raise Exception( f'Object "{ object.name }" has no mesh. If you want to export this object without mesh - uncheck the "Export geometry" option' )

    bmesh.ops.triangulate( mesh, faces = mesh.faces )

    # Delete loose vertices
    loose_vertices = [ vert for vert in mesh.verts if not vert.link_faces ]

    if len( loose_vertices ) :
        bmesh.ops.delete( mesh, geom = loose_vertices )

    del loose_vertices

    # Perform vertex duplication if single vertex links with multiple edges and in each link have different UV coordinates
    verts_data = {}
    verts_to_uv_tuple = {}
    tris = mesh.calc_loop_triangles()
    uv_layers = list( mesh.loops.layers.uv.values() )
    min_vert_coord = [ +math.inf, +math.inf, +math.inf ]
    max_vert_coord = [ -math.inf, -math.inf, -math.inf ]

    for tri_loops in tris :
        for tri_loop in tri_loops :
            vert = tri_loop.vert
            uv_tuple = tuple()

            for uv_layer in uv_layers :
                uv_tuple = uv_tuple + tri_loop[ uv_layer ].uv.to_tuple()

            if vert not in verts_data :
                vert_uv_tuples, uv_tuple_verts = verts_data[ vert ] = ( [], [] )

                verts_to_uv_tuple[ vert ] = uv_tuple
                vert_uv_tuples.append( uv_tuple )
                uv_tuple_verts.append( vert )

                min_vert_coord[ 0 ] = min( min_vert_coord[ 0 ], vert.co.y )
                min_vert_coord[ 1 ] = min( min_vert_coord[ 1 ], vert.co.z )
                min_vert_coord[ 2 ] = min( min_vert_coord[ 2 ], vert.co.x )
                max_vert_coord[ 0 ] = max( max_vert_coord[ 0 ], vert.co.y )
                max_vert_coord[ 1 ] = max( max_vert_coord[ 1 ], vert.co.z )
                max_vert_coord[ 2 ] = max( max_vert_coord[ 2 ], vert.co.x )
            else :
                vert_uv_tuples, uv_tuple_verts = verts_data[ vert ]

            if uv_tuple not in vert_uv_tuples :
                vert = bmesh.utils.face_vert_separate( tri_loop.face, vert )

                verts_to_uv_tuple[ vert ] = uv_tuple
                vert_uv_tuples.append( uv_tuple )
                uv_tuple_verts.append( vert )
            else :
                vert = uv_tuple_verts[ vert_uv_tuples.index( uv_tuple ) ]

                if tri_loop.vert != vert :
                    temporary_vert = bmesh.utils.face_vert_separate( tri_loop.face, tri_loop.vert )
                    bmesh.utils.vert_splice( temporary_vert, vert )

    del verts_data

    if len( mesh.verts ) > 65536 :
        raise Exception( f'Object "{ object.name }" exceeds 65536 vertices' )

# 09-01E-000 -- Start
    gbx.nat32( 0x0901E000 )
# 09-006-00E -- Start
    gbx.nat32( 0x0900600E )
    gbx.nat32( 0x00000078 )
    gbx.nat32( len( uv_layers ) )
    gbx.nat32( len( mesh.verts ) )
    gbx.nat32( 0x00000000 )

    # Recalculate mesh normals and vertex indices after vertex duplication
    mesh.verts.index_update()
    mesh.normal_update()

    loops = []
    tris = mesh.calc_loop_triangles()

    for tri_loops in tris :
        for tri_loop in tri_loops :
            loops.append( tri_loop.vert.index )

    for uv_index in range( len( uv_layers ) ) :
        uv_tuple_offset = 2 * uv_index

        gbx.nat32( 0x00000000 )

        for vert in mesh.verts :
            uv_tuple = verts_to_uv_tuple[ vert ]

            gbx.real( uv_tuple[ 0 + uv_tuple_offset ] )
            gbx.real( uv_tuple[ 1 + uv_tuple_offset ] )

    half_diag = \
    (
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
        gbx.real( vert.co.y )
        gbx.real( vert.co.z )
        gbx.real( vert.co.x )
        gbx.real( vert.normal.y )
        gbx.real( vert.normal.z )
        gbx.real( vert.normal.x )

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