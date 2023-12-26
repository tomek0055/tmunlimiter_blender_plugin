import bpy

class TMUnlimiter_Variation( bpy.types.PropertyGroup ) :
    def poll_object( self, object: bpy.types.Object ) :
        if object.type in { "MESH", "LIGHT" } :
            return True

        child_objects = object.children

        for child_object in child_objects :
            if self.poll_object( child_object ) :
                return True

        return False

    name: bpy.props.StringProperty( name = "Variation Name" )
    model: bpy.props.PointerProperty( name = "Model", type = bpy.types.Object, poll = poll_object )
    trigger: bpy.props.PointerProperty( name = "Trigger", type = bpy.types.Object, poll = poll_object )

    def validate_model( self ) :
        if not self.model :
            return ( False, "Model must be chosen" )

        return ( True, None )

    def validate_trigger( self ) :
        if not self.trigger :
            return ( False, "Trigger must be chosen" )

        return ( True, None )