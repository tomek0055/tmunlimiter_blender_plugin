bl_info = {
    "name" : "TrackMania GameBox format exporter",
    "author": "Tomek0055",
    "version" : (1, 0, 0),
    "blender" : (3, 1, 0),
    "doc_url" : "https://github.com/kemot0055/io_scene_gbx",
    "support" : "COMMUNITY",
    "category" : "Import-Export",
    "location" : "File > Import-Export",
}

import bpy
from .export_gbx import ExportSolidGbx

def menu_func_export( self, context ):
    self.layout.operator( ExportSolidGbx.bl_idname )

def register() :
    bpy.utils.register_class( ExportSolidGbx )
    bpy.types.TOPBAR_MT_file_export.append( menu_func_export )

def unregister() :
    bpy.types.TOPBAR_MT_file_export.remove( menu_func_export )
    bpy.utils.unregister_class( ExportSolidGbx )

if __name__ == "__main__" :
    register()