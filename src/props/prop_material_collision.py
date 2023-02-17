from ..material_collision.default_collision_materials import DEFAULT_COLLISION_MATERIALS
import bpy

class TMUnlimiterMaterialCollisionProps( bpy.types.PropertyGroup ) :

    is_collidable: bpy.props.BoolProperty(
        name = "Is collidable",
    )

    collision_material: bpy.props.EnumProperty(
        name = "Collision material",
        items = DEFAULT_COLLISION_MATERIALS,
    )

class TMUnlimiterMaterialCollision( bpy.types.Panel ) :
    bl_idname = "UNLIMITER_PT_material_collision"
    bl_label = "TMUnlimiter - Collision properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll( self, context: bpy.context ) :
        return context.object.unlimiter_object_settings.can_export_collision and context.material is not None

    def draw( self, context: bpy.context ) :
        data: TMUnlimiterMaterialCollision = context.material.unlimiter_material_collision

        self.layout.prop( data, "is_collidable" )

        if data.is_collidable :
            self.layout.prop( data, "collision_material" )

def __register__() :
    bpy.utils.register_class( TMUnlimiterMaterialCollisionProps )
    bpy.utils.register_class( TMUnlimiterMaterialCollision )

    bpy.types.Material.unlimiter_material_collision = bpy.props.PointerProperty(
        type = TMUnlimiterMaterialCollisionProps
    )

def __unregister__() :
    bpy.utils.unregister_class( TMUnlimiterMaterialCollision )
    bpy.utils.unregister_class( TMUnlimiterMaterialCollisionProps )