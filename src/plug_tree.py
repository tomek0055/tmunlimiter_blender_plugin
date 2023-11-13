from .props.prop_object_settings import TMUnlimiterObjectSettings
from .plug_visual_3d import plug_visual_3d
from .gx_light_ball import gx_light_ball
from .gx_light_spot import gx_light_spot
from .plug_surface import plug_surface
from .blender_gbx import GbxArchive
from math import pi

import mathutils
import bpy

def plug_tree_from_collection( gbx: GbxArchive, collection: bpy.types.Collection ) :
    gbx.nat32( 0x0904f000 )

    gbx.nat32( 0x0904f00d )
    gbx.mw_id( collection.name )
    gbx.nat32( 0xffffffff )

    flags = 0x00004000
    objects  = list( filter( lambda object: object.parent is None, collection.all_objects ) )

    if len( objects ) :
        gbx.nat32( 0x0904f006 )
        gbx.nat32( 0x0000000a )
        gbx.nat32( len( objects ) )

        for object in objects :
            was_valid_ref, child_flags, _ = gbx.mw_ref( plug_tree_from_object, object )

            if was_valid_ref :
                flags |= child_flags & 0xfffffffb

    gbx.nat32( 0x0904f01a )
    gbx.nat32( flags )
    gbx.nat32( 0xfacade01 )

def plug_tree_from_object( gbx: GbxArchive, object: bpy.types.Object ) :
    if object.type == "LIGHT" :
        gbx.nat32( 0x09062000 )
    else :
        gbx.nat32( 0x0904f000 )

    gbx.nat32( 0x0904f00d )
    gbx.mw_id( object.name )
    gbx.nat32( 0xffffffff )

    flags = 0x00004004
    scale = object.scale.copy()
    rotation = object.rotation_euler.copy()
    has_visual = False
    is_collidable = False

    if len( object.children ) :
        gbx.nat32( 0x0904f006 )
        gbx.nat32( 0x0000000a )
        gbx.nat32( len( object.children ) )

        for children in object.children :
            was_valid_ref, child_flags, _ = gbx.mw_ref( plug_tree_from_object, children )

            if was_valid_ref :
                flags |= child_flags

    if object.type == "LIGHT" :
        light: bpy.types.Light = object.data

        if light.type == "POINT" :
            func = gx_light_ball
        elif light.type == "SPOT" :
            func = gx_light_spot
            rotation.x += pi / 2
        else :
            raise Exception( f'Not supported light type: "{ light.type }"' )

        gbx.nat32( 0x09062001 )
        gbx.mw_ref( func, light )
        gbx.nat32( 0xffffffff )
    else :
        object_settings: TMUnlimiterObjectSettings = object.unlimiter_object_settings
        gbx.nat32( 0x0904f014 )

        if object_settings.can_export_geometry :
            has_visual, _, _ = gbx.mw_ref( plug_visual_3d, object )
            gbx.nat32( 0xffffffff )

            if has_visual :
                object_settings.archive_material( gbx )
            else :
                gbx.nat32( 0xffffffff )
        else :
            gbx.nat32( 0xffffffff )
            gbx.nat32( 0xffffffff )
            gbx.nat32( 0xffffffff )

        if object_settings.can_export_collision :
            is_collidable, _, _ = gbx.mw_ref( plug_surface, object )
        else :
            gbx.nat32( 0xffffffff )

        gbx.nat32( 0xffffffff )

    if has_visual :
        flags |= 0x00000008

    if is_collidable :
        flags |= 0x00000080

    gbx.nat32( 0x0904f01a )
    gbx.nat32( flags )

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
    gbx.real( object.location.y )
    gbx.nat32( 0xfacade01 )

    return flags