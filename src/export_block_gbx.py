from .props.prop_material_collision import (
    __register__ as material_collision_register,
    __unregister__ as material_collision_unregister,
)

from .props.prop_object_settings import (
    __register__ as object_settings_register,
    __unregister__ as object_settings_unregister,
)

from .unlimiter_block_v1 import (
    unlimiter_block_v1,
    CLASS_ID,
)

from bpy_extras.io_utils import ExportHelper
from .blender_gbx import BlenderGbx
import bpy

class ExportBlockGbx( bpy.types.Operator, ExportHelper ):
    """Save as *.Block.Gbx file, to enable export, switch to object mode"""

    bl_label = "Export *.Block.Gbx file"
    bl_idname = "export_scene.block_v1_gbx"
    bl_options = { "PRESET" }

    filter_glob : bpy.props.StringProperty(
        default = "*.Block.Gbx",
        options = { "HIDDEN" },
    )
    
    block_id : bpy.props.StringProperty(
        name = "Block ID",
        description = "Block unique identifier",
    )

    block_author : bpy.props.StringProperty(
        name = "Block author",
        description = "Block author name",
    )

    spawn_point : bpy.props.FloatVectorProperty(
        name = "Spawn point",
        description = "Vehicle spawn location",
    )

    @classmethod
    def poll( self, context : bpy.context ) :
        return context.mode == "OBJECT"

    def invoke( self, context : bpy.context, _event ) :
        if not self.filepath :
            self.filepath = "Model.Block.Gbx"

        context.window_manager.fileselect_add( self )
        return { "RUNNING_MODAL" }

    def execute( self, context : bpy.context ) :
        gbx = BlenderGbx(
            CLASS_ID,
            context.evaluated_depsgraph_get()
        )

        unlimiter_block_v1(
            gbx,
            self.block_id,
            self.block_author,
            self.spawn_point,
            context.active_object,
        )

        gbx.do_save( self.properties.filepath )
        return { "FINISHED" }

def add_export( self, context ) :
    self.layout.operator( ExportBlockGbx.bl_idname )

def __register__() :
    bpy.utils.register_class( ExportBlockGbx )

    object_settings_register()
    material_collision_register()

    bpy.types.TOPBAR_MT_file_export.append( add_export )

def __unregister__() :
    bpy.types.TOPBAR_MT_file_export.remove( add_export )

    material_collision_unregister()
    object_settings_unregister()

    bpy.utils.unregister_class( ExportBlockGbx )