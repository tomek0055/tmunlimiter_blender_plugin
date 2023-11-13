import bpy

class TMUnlimiter_Variation( bpy.types.PropertyGroup ) :
    def poll_object( self, object: bpy.types.Object ) :
        return type( object.data ) == bpy.types.Mesh

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