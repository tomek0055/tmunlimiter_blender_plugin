from .plug_visual_3d import (
    plug_visual_3d,
)

from .plug_surface import (
    plug_surface,
)

from .gbx import Gbx
import mathutils
import bpy

def plug_tree_from_collection( gbx : Gbx, collection : bpy.types.Collection ) :
    objects = list( filter( lambda object : object.parent is None, collection.all_objects ) )

# 09-04F-000 -- Start
    gbx.nat32( 0x0904F000 )

# 09-04F-00D -- Start
    gbx.nat32( 0x0904F00D )
    gbx.mw_id( collection.name )
    gbx.nat32( 0xFFFFFFFF )
# 09-04F-00D -- End

# 09-04F-006 -- Start
    if len( objects ) :
        gbx.nat32( 0x0904F006 )
        gbx.nat32( 0x0000000A )
        gbx.nat32( len( objects ) )

        for object in objects :
            gbx.mw_ref( plug_tree_from_object, object )
# 09-04F-006 -- End

    gbx.nat32( 0xFACADE01 )
# 09-04F-000 -- End

def plug_tree_from_object( gbx : Gbx, object : bpy.types.Object ) :
# 09-04F-000 -- Start
    gbx.nat32( 0x0904F000 )

# 09-04F-00D -- Start
    gbx.nat32( 0x0904F00D )
    gbx.mw_id( object.name )
    gbx.nat32( 0xFFFFFFFF )
# 09-04F-00D -- End

# 09-04F-006 -- Start
    if len( object.children ) :
        gbx.nat32( 0x0904F006 )
        gbx.nat32( 0x0000000A )
        gbx.nat32( len( object.children ) )

        for children in object.children :
            gbx.mw_ref( plug_tree_from_object, children )
# 09-04F-006 -- End
# 09-04F-01A -- Start
    gbx.nat32( 0x0904F01A )
    gbx.nat32( 0x0000400C )

    scale = object.scale.copy()
    rotation = object.rotation_euler.copy()

    scale.y = object.scale.z
    scale.z = object.scale.y
    rotation.y = object.rotation_euler.z
    rotation.z = -object.rotation_euler.y

    matrix = mathutils.Matrix.LocRotScale(
        None, rotation, scale
    )

    gbx.real( matrix[ 0 ].x )
    gbx.real( matrix[ 0 ].y )
    gbx.real( matrix[ 0 ].z )
    gbx.real( matrix[ 1 ].x )
    gbx.real( matrix[ 1 ].y )
    gbx.real( matrix[ 1 ].z )
    gbx.real( matrix[ 2 ].x )
    gbx.real( matrix[ 2 ].y )
    gbx.real( matrix[ 2 ].z )
    gbx.real( object.location.x )
    gbx.real( object.location.z )
    gbx.real( -object.location.y )
# 09-04F-01A -- End
# 09-04F-016 -- Start
    gbx.nat32( 0x0904F016 )
    gbx.mw_ref( plug_visual_3d, object )
    gbx.nat32( 0xFFFFFFFF )
    gbx.mw_ref( plug_surface, object )
    gbx.nat32( 0xFFFFFFFF )
# 09-04F-016 -- End
    gbx.nat32( 0xFACADE01 )
# 09-04F-000 -- End