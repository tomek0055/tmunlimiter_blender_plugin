from __future__ import annotations

import bpy

def poll_object( self, object: bpy.types.Object ) :
    if object.type == "MESH" :
        return True
    elif object.type == "EMPTY" :
        pass
    else:
        return False

    child_objects = object.children

    for child_object in child_objects :
        if poll_object( self, child_object ) :
            return True

    return False

class TMUnlimiter_Variation( bpy.types.PropertyGroup ) :
    name: bpy.props.StringProperty( name = "Variation Name" )
    model: bpy.props.PointerProperty( name = "Model", type = bpy.types.Object, poll = poll_object )
    trigger: bpy.props.PointerProperty( name = "Trigger", type = bpy.types.Object, poll = poll_object )

    def copy_from( self, other: TMUnlimiter_Variation ) :
        self.name = other.name
        self.model = other.model
        self.trigger = other.trigger

    def validate_model( self ) :
        if not self.model :
            return ( False, "Model must be chosen" )

        return ( True, None )

    def validate_trigger( self ) :
        if not self.trigger :
            return ( False, "Trigger must be chosen" )

        return ( True, None )