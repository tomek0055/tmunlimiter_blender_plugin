bl_info = {
    "name" : "TrackMania GameBox format exporter",
    "author": "Tomek0055",
    "version" : (1, 0, 0),
    "blender" : (3, 1, 2),
    "doc_url" : "https://github.com/kemot0055/io_scene_gbx",
    "support" : "COMMUNITY",
    "category" : "Import-Export",
    "location" : "File > Import-Export",
}

from .export_block_gbx import (
    __register__ as export_block_gbx_register,
    __unregister__ as export_block_gbx_unregister,
)

from .export_solid_gbx import (
    __register__ as export_solid_gbx_register,
    __unregister__ as export_solid_gbx_unregister,
)

def register() :
    export_solid_gbx_register()
    export_block_gbx_register()

def unregister() :
    export_solid_gbx_unregister()
    export_block_gbx_unregister()

if __name__ == "__main__" :
    register()