from __future__ import annotations

from .variation import TMUnlimiter_Variation
import bpy

class TMUnlimiter_Variants( bpy.types.PropertyGroup ) :
    selected_variation_index: bpy.props.IntProperty( options = { "HIDDEN", "SKIP_SAVE" } )
    ground_variations: bpy.props.CollectionProperty( type = TMUnlimiter_Variation )
    air_variations: bpy.props.CollectionProperty( type = TMUnlimiter_Variation )

    def copy_from( self, other: TMUnlimiter_Variants ) :
        self.selected_variation_index = other.selected_variation_index

        for ground_variation in self.ground_variations :
            ground_variation.copy_from( other.ground_variations )

        for air_variation in self.air_variations :
            air_variation.copy_from( other.air_variations )