bl_info = {
    "name" : "TrackMania Unlimiter: Custom Block exporter",
    "author": "Tomek0055",
    "version" : (1, 0, 0),
    "blender" : (4, 0, 0),
    "doc_url" : "https://github.com/tomek0055/io_scene_gbx",
    "support" : "COMMUNITY",
    "category" : "Import-Export",
    "location" : "File > Import-Export",
}

from .props.prop_material_collision import (
    __register__ as material_collision_register,
    __unregister__ as material_collision_unregister,
)

from .props.prop_object_settings import (
    __register__ as object_settings_register,
    __unregister__ as object_settings_unregister,
)

from .props.block_definitions_panel import (
    __register__ as block_definitions_panel_register,
    __unregister__ as block_definitions_panel_unregister,
)

def register() :
    object_settings_register()
    material_collision_register()
    block_definitions_panel_register()

def unregister() :
    object_settings_unregister()
    material_collision_unregister()
    block_definitions_panel_unregister()

if __name__ == "__main__" :
    register()