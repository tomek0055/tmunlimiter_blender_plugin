from .props.prop_object_settings import TMUnlimiterObjectSettings
from .plug_visual_3d import plug_visual_3d
from .gx_light_ball import gx_light_ball
from .gx_light_spot import gx_light_spot
from .plug_surface import plug_surface
from .blender_gbx import GbxArchive
from math import pi

import mathutils
import bpy

def _get_plug_tree_class_identifier( object: bpy.types.Object ) :
    if object.type == "LIGHT" :
        light_data: bpy.types.Light = object.data

        if light_data.type in { "POINT", "SPOT" } :
            return 0x09_062_000

        raise Exception( f'The selected light type "{ light_data.type }" is not supported by the game' )

    if object.type not in { "MESH", "EMPTY" } :
        raise Exception( f'The type "{ object.type }" of an object "{ object.name }" is not supported by the game or the exporter' )

    if object.type == "EMPTY" and object.unlimiter_object_settings.is_visual_mip :
        return 0x09_015_000

    return 0x09_04f_000

def plug_tree_from_object( gbx: GbxArchive, object: bpy.types.Object ) :
    object_settings: TMUnlimiterObjectSettings = object.unlimiter_object_settings

    plug_tree_class_identifier = _get_plug_tree_class_identifier( object )
    gbx.nat32( plug_tree_class_identifier )

    if object_settings.can_export_object_name :
        gbx.nat32( 0x0904f00d )
        gbx.mw_id( object.name )
        gbx.nat32( 0xffffffff )

    flags = 0x00004004
    scale = object.scale.copy()
    rotation = object.rotation_euler.copy()
    has_visual = False
    is_collidable = False

    child_objects = list( filter( lambda object: not object.unlimiter_object_settings.exclude_from_export, object.children ) )
    child_count = len( child_objects )

    if child_count :
        if plug_tree_class_identifier == 0x09_015_000 :
            child_objects.sort( key = lambda object: object.unlimiter_object_settings.visual_mip_distance )

            gbx.nat32( 0x09015002 )
            gbx.nat32( child_count )

            for child_object in child_objects :
                gbx.real( child_object.unlimiter_object_settings.visual_mip_distance )
                valid_ref, child_flags, _ = gbx.mw_ref( plug_tree_from_object, child_object )

                if valid_ref :
                    flags |= child_flags
        else :
            gbx.nat32( 0x0904f006 )
            gbx.nat32( 0x0000000a )
            gbx.nat32( child_count )

            for child_object in child_objects :
                valid_ref, child_flags, _ = gbx.mw_ref( plug_tree_from_object, child_object )

                if valid_ref :
                    flags |= child_flags

    if object.type == "LIGHT" :
        light: bpy.types.Light = object.data

        if light.type == "POINT" :
            func = gx_light_ball
        elif light.type == "SPOT" :
            func = gx_light_spot
            rotation.x += pi / 2

        gbx.nat32( 0x09062001 )
        gbx.mw_ref( func, light )
        gbx.nat32( 0xffffffff )
    elif object.type == "MESH" :
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

        if scale.x != 1.0 or scale.y != 1.0 or scale.z != 1.0 :
            raise Exception( f'An object "{ object.name }" has a collision with a scale other than 1.0 - Please apply a scale transform to your object' )

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
    gbx.real( -object.location.y )
    gbx.nat32( 0xfacade01 )

    return flags