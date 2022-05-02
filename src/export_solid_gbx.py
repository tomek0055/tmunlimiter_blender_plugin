from .plug_tree import plug_tree_from_collection
from bpy_extras.io_utils import ExportHelper
from .gbx import Gbx
import bpy

def export( context : bpy.types.Context, **keywords ) :
    gbx = Gbx( 0x09005000, {
        "plug_surface" : lambda *_, **__ : False
    } )

    if keywords[ "use_active_collection" ] :
        collection = context.collection
    else :
        collection = context.scene.collection

# 0x09005000 -- start
    gbx.nat32( 0x09005000 )
    gbx.nat32( 0x00000001 )
# 0x09005011 -- start
    gbx.nat32( 0x09005011 )
    gbx.nat32( 0x00000000 )
    gbx.nat32( 0x00000000 )
    gbx.mw_ref( plug_tree_from_collection, collection )
# 0x09005011 -- end
    gbx.nat32( 0xFACADE01 )
# 0x09005000 -- end

    gbx.do_save( keywords[ "filepath" ] )
    return { "FINISHED" }

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
        return export( context, **self.as_keywords() )