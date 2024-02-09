from __future__ import annotations
from .blender_gbx import GbxArchive
import bpy

class TMUnlimiter_BlockUnit( bpy.types.PropertyGroup ) :
    def __validate_object__( self, object: bpy.types.Object ) :
        return self.validate( object_to_evaluate = object )[ 0 ]

    object: bpy.props.PointerProperty( type = bpy.types.Object, poll = __validate_object__ )

    def archive( self, gbx: GbxArchive ) :
        offset = self.calculate_offset()

        gbx.nat32( offset[ 0 ] )
        gbx.nat32( offset[ 1 ] )
        gbx.nat32( offset[ 2 ] )

    def validate( self, **kwargs ) :
        object_to_evaluate: bpy.types.Object = self.object

        if "object_to_evaluate" in kwargs :
            object_to_evaluate = kwargs[ "object_to_evaluate" ]

            if type( object_to_evaluate ) != bpy.types.Object :
                return ( False, "Object to evaluate is not an object from blender" )

        if not object_to_evaluate :
            return ( False, f'Block unit object is not defined' )

        if object_to_evaluate.type != "EMPTY" :
            return ( False, f'Block unit object "{ object_to_evaluate.name }" must be an empty' )

        if object_to_evaluate.empty_display_type != "CUBE" :
            return ( False, f'Block unit object "{ object_to_evaluate.name }" must be displayed as a cube' )

        if object_to_evaluate.empty_display_size != 1 :
            return ( False, f'Block unit object "{ object_to_evaluate.name }" must have display size set to 1' )

        if object_to_evaluate.scale.x <= 0 or object_to_evaluate.scale.y <= 0 or object_to_evaluate.scale.z <= 0 :
            return ( False, f'Block unit object "{ object_to_evaluate.name }" cannot have scale set to zero or below' )

        if object_to_evaluate.location.x < object_to_evaluate.scale.x :
            return ( False, f'Block unit object "{ object_to_evaluate.name }" cannot have location set below X scale' )

        if object_to_evaluate.location.y < object_to_evaluate.scale.y :
            return ( False, f'Block unit object "{ object_to_evaluate.name }" cannot have location set below Y scale' )

        if object_to_evaluate.location.z < object_to_evaluate.scale.z :
            return ( False, f'Block unit object "{ object_to_evaluate.name }" cannot have location set below Z scale' )

        return ( True, None )

    def calculate_offset( self ) :
        return \
        (
            int( ( self.object.location.y - self.object.scale.y ) / ( self.object.scale.y * 2 ) ),
            int( ( self.object.location.z - self.object.scale.z ) / ( self.object.scale.z * 2 ) ),
            int( ( self.object.location.x - self.object.scale.x ) / ( self.object.scale.x * 2 ) ),
        )

    def copy_from( self, other: TMUnlimiter_BlockUnit ) :
        self.object = other.object