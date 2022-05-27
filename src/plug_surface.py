from .blender_gbx import BlenderGbx
import bmesh
import bpy

def plug_surface_geom_mesh( gbx : BlenderGbx, object : bpy.types.Object ) -> list[ bpy.types.Material ] :
    gbx.nat32( 0x0900F000 )
    gbx.nat32( 0x0900F002 )

    mesh_data : bpy.types.Mesh = object.data

    mesh = bmesh.new()
    mesh.from_object( object, gbx.depsgraph )
    bmesh.ops.triangulate( mesh, faces = mesh.faces )

    faces : list[ bmesh.types.BMFace ] = list(
        filter(
            lambda face : \
                mesh_data.materials[ face.material_index ] is not None \
                    and \
                mesh_data.materials[ face.material_index ].unlimiter_material_collision.is_collidable,
            
            mesh.faces
        )
    )

    vertices_index = set()
    material_translation_table : dict[ int, ( int, bpy.types.Material ) ] = {}

    for face in faces :
        loops : list[ bmesh.types.BMLoop ] = face.loops

        for loop in loops :
            vertices_index.add( loop.vert.index )

        material_index = face.material_index

        if not material_index in material_translation_table :
            material_translation_table[ material_index ] = (
                len( material_translation_table ),
                mesh_data.materials[ material_index ],
            )

    gbx.nat32( 7 )
    gbx.nat32( 1 )

    # verts
    vertex_translation_table : dict[ int, int ] = {}

    mesh.verts.ensure_lookup_table()
    gbx.nat32( len( vertices_index ) )

    for vertex_index in vertices_index :
        vertex = mesh.verts[ vertex_index ]

        gbx.real( vertex.co.x )
        gbx.real( vertex.co.z )
        gbx.real( -vertex.co.y )

        vertex_translation_table[ vertex_index ] = len( vertex_translation_table )

    # faces
    gbx.nat32( len( faces ) )

    for face in faces :
        gbx.real( face.normal.x )
        gbx.real( face.normal.z )
        gbx.real( -face.normal.y )
        gbx.real( 0 )
        
        loops : list[ bmesh.types.BMLoop ] = face.loops

        for loop in loops :
            gbx.nat32( vertex_translation_table[ loop.vert.index ] )
        
        gbx.nat16( material_translation_table[ face.material_index ][ 0 ] )
        gbx.nat16( 0 )

    # zero list
    gbx.nat32( 0 )
    # this field is ignored in "Mesh" surface type
    gbx.nat16( 0 )
    # naura
    gbx.nat32( 0xFACADE01 )

    return list(
        map(
            lambda key : material_translation_table[ key ][ 1 ],
            material_translation_table
        )
    )

def plug_surface( gbx : BlenderGbx, object : bpy.types.Object ) :
    gbx.nat32( 0x0900C000 )
    gbx.nat32( 0x0900C000 )
    _, materials = gbx.mw_ref( plug_surface_geom_mesh, object )

    gbx.nat32( len( materials ) )

    for material in materials :
        gbx.nat32( 0 )
        gbx.nat16( int( material.unlimiter_material_collision.collision_material ) )

    gbx.nat32( 0xFACADE01 )