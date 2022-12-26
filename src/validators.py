import bpy

def validate_plug_visual_3d( object: bpy.types.Object ) -> bool :
    return object.type == "MESH" and len( object.data.polygons ) > 0

def validate_plug_surface( object: bpy.types.Object ) -> bool :
    return \
        validate_plug_visual_3d( object ) \
            and \
        len(
            list(
                filter(
                    lambda material: \
                        material is not None \
                            and \
                        material.unlimiter_material_collision.is_collidable,

                    object.data.materials
                )
            )
        ) > 0