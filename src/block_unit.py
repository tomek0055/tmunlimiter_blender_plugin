from __future__ import annotations
from .blender_gbx import GbxArchive
import bpy

class TMUnlimiter_BlockUnit( bpy.types.PropertyGroup ) :
    @staticmethod
    def static_object_validate( object: bpy.types.Object ) :
        if not object :
            return ( False, f'Block unit object is not defined' )

        if object.type != "EMPTY" :
            return ( False, f'Block unit object "{ object.name }" must be an empty' )

        if object.empty_display_type != "CUBE" :
            return ( False, f'Block unit object "{ object.name }" must be displayed as a cube' )

        if object.empty_display_size != 1 :
            return ( False, f'Block unit object "{ object.name }" must have display size set to 1' )

        if object.scale.x <= 0 or object.scale.y <= 0 or object.scale.z <= 0 :
            return ( False, f'Block unit object "{ object.name }" cannot have scale set to zero or below' )

        if object.location.x < object.scale.x :
            return ( False, f'Block unit object "{ object.name }" cannot have location set below X scale' )

        if object.location.y < object.scale.y :
            return ( False, f'Block unit object "{ object.name }" cannot have location set below Y scale' )

        if object.location.z < object.scale.z :
            return ( False, f'Block unit object "{ object.name }" cannot have location set below Z scale' )

        return ( True, None )

    @staticmethod
    def static_calculate_offset( object: bpy.types.Object ) :
        return \
        (
            int( ( object.location.y - object.scale.y ) / ( object.scale.y * 2 ) ),
            int( ( object.location.z - object.scale.z ) / ( object.scale.z * 2 ) ),
            int( ( object.location.x - object.scale.x ) / ( object.scale.x * 2 ) ),
        )
    
    def __poll_object__( self, object: bpy.types.Object ) :
        return TMUnlimiter_BlockUnit.static_object_validate( object )[ 0 ]

    object: bpy.props.PointerProperty( type = bpy.types.Object, poll = __poll_object__ )

    def archive( self, gbx: GbxArchive ) :
        offset = self.calculate_offset()

        gbx.nat32( offset[ 0 ] )
        gbx.nat32( offset[ 1 ] )
        gbx.nat32( offset[ 2 ] )

    def validate( self ) :
        return TMUnlimiter_BlockUnit.static_object_validate( self.object )

    def calculate_offset( self ) :
        return TMUnlimiter_BlockUnit.static_calculate_offset( self.object )

    def copy_from( self, other: TMUnlimiter_BlockUnit ) :
        self.object = other.object