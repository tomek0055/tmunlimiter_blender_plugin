from .variation import TMUnlimiter_Variation
import bpy

class TMUnlimiter_Variants( bpy.types.PropertyGroup ) :
    selected_variation_index: bpy.props.IntProperty( options = { "HIDDEN", "SKIP_SAVE" } )
    ground_variations: bpy.props.CollectionProperty( type = TMUnlimiter_Variation )
    air_variations: bpy.props.CollectionProperty( type = TMUnlimiter_Variation )