from bpy_extras.io_utils import ExportHelper
from .blender_gbx import BlenderGbx
from .plug_solid import plug_solid
import bpy

class ExportSolidGbx( bpy.types.Operator, ExportHelper ):
    """Save as *.Solid.Gbx File"""

    bl_label = "Export *.Solid.Gbx file"
    bl_idname = "export_scene.gbx"
    bl_options = { "PRESET" }

    filter_glob : bpy.props.StringProperty(
        default = "*.Solid.Gbx",
        options = { "HIDDEN" },
    )

    use_active_collection : bpy.props.BoolProperty(
        name = "Active Collection",
        default = False,
        description = "Export only objects from the active collection",
    )

    filename_ext = ".Solid.Gbx"
    check_extension = False

    def execute( self, context ) :
        gbx = BlenderGbx(
            0x09005000,
            context.evaluated_depsgraph_get(),
            {
                "plug_surface" : lambda *_, **__ : False
            }
        )

        if self.use_active_collection :
            collection = context.collection
        else :
            collection = context.scene.collection
        
        plug_solid( gbx, collection )
        gbx.do_save( self.filepath )

        return { "FINISHED" }

def add_solid_gbx_export( self, context ) :
    self.layout.operator( ExportSolidGbx.bl_idname )

def __register__() :
    bpy.utils.register_class( ExportSolidGbx )
    bpy.types.TOPBAR_MT_file_export.append( add_solid_gbx_export )

def __unregister__() :
    bpy.types.TOPBAR_MT_file_export.remove( add_solid_gbx_export )
    bpy.utils.unregister_class( ExportSolidGbx )