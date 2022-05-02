from .gbx import Gbx
import bmesh
import bpy

def plug_visual_3d( gbx : Gbx, object : bpy.types.Object ) :
    mesh = bmesh.new()
    mesh.from_mesh( object.data )
    bmesh.ops.triangulate( mesh, faces = mesh.faces )

    uv_layers = mesh.loops.layers.uv.values()
    triangles_loops = mesh.calc_loop_triangles()

    vertices_uv_tuples = [
        (
            [ {} for _ in range( len( uv_layers ) ) ],
            [ vert ]
        )
        for vert in mesh.verts
    ]

    uvs = [ {} for _ in range( len( uv_layers ) ) ]
    loops = []

    for triangle_loops in triangles_loops :
        for loop in triangle_loops :
            vert = loop.vert

            for uv_idx, uv_layer in enumerate( uv_layers ) :
                uv_layers_tuples, vertices = vertices_uv_tuples[ vert.index ]
                uv_layer_tuples = uv_layers_tuples[ uv_idx ]
                uv_tuple = loop[ uv_layer ].uv.to_tuple()

                if not uv_tuple in uv_layer_tuples :
                    uv_layer_tuples_size = len( uv_layer_tuples )

                    if uv_layer_tuples_size < len( vertices ) :
                        vert = vertices[ uv_layer_tuples_size ]
                    else :
                        vert = mesh.verts.new( vert.co, vert )
                        vert.index = len( mesh.verts ) - 1
                        vertices.append( vert )

                    uv_layer_tuples[ uv_tuple ] = vert
                    uvs[ uv_idx ][ vert.index ] = uv_tuple
                else :
                    vert = uv_layer_tuples[ uv_tuple ]

            loops.append( vert.index )

    if len( mesh.verts ) > 65535 :
        raise "Object exceeds 65535 vertices"

# 09-01E-000 -- Start
    gbx.nat32( 0x0901E000 )
# 09-006-00E -- Start
    gbx.nat32( 0x0900600E )
    gbx.nat32( 0x00000038 )
    gbx.nat32( len( uv_layers ) )
    gbx.nat32( len( mesh.verts ) )
    gbx.nat32( 0x00000000 )

    for uv_idx in range( len( uv_layers ) ) :
        gbx.nat32( 0x00000000 )

        uvs = uvs[ uv_idx ]

        for vertex_idx in range( len( mesh.verts ) ) :
            uv_tuple = uvs.get( vertex_idx )

            if uv_tuple is None :
                uv_tuple = ( 0, 0 )

            gbx.real( uv_tuple[ 0 ] )
            gbx.real( uv_tuple[ 1 ] )

    gbx.real( object.dimensions.x / 2 )
    gbx.real( object.dimensions.z / 2 )
    gbx.real( object.dimensions.y / 2 )
    gbx.real( object.dimensions.x / 2 )
    gbx.real( object.dimensions.z / 2 )
    gbx.real( object.dimensions.y / 2 )
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