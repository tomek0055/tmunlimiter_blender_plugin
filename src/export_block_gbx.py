from .props.prop_material_collision import (
    __register__ as material_collision_register,
    __unregister__ as material_collision_unregister,
)

from .props.prop_object_settings import (
    __register__ as object_settings_register,
    __unregister__ as object_settings_unregister,
)

from .unlimiter_block import (
    unlimiter_block,
    CLASS_ID,
)

from bpy_extras.io_utils import ExportHelper
from traceback import print_exception
from .blender_gbx import GbxArchive
import bpy

class ExportBlockGbx( bpy.types.Operator, ExportHelper ):
    """Save as *.Block.Gbx file, to enable export, switch to object mode"""

    bl_label = "Export *.Block.Gbx file"
    bl_idname = "export_scene.block_v1_gbx"
    bl_options = { "PRESET" }

    filter_glob: bpy.props.StringProperty(
        default = "*.Block.Gbx",
        options = { "HIDDEN" },
    )
    
    block_id: bpy.props.StringProperty(
        name = "Block ID",
        description = "Block unique identifier",
    )

    block_author: bpy.props.StringProperty(
        name = "Block author",
        description = "Block author name",
    )

    spawn_point: bpy.props.FloatVectorProperty(
        name = "Spawn point",
        description = "Vehicle spawn location",
    )

    root_object_kind: bpy.props.EnumProperty(
        name = "Root object",
        items = [
            (
                "SceneCollection",
                "Use current scene collection",
                "Use current scene collection as a root object in the model hierarchy",
            ),
            (
                "SelectedCollection",
                "Use selected collection",
                "Use selected collection as a root object in the model hierarchy",
            ),
            (
                "SelectedObject",
                "Use selected object",
                "Use selected object as a root object in the model hierarchy",
            ),
        ],
        description = "This option determines what resource could be used as a root object in the model hierarchy",
    )

    check_extension = None

    @classmethod
    def poll( self, context: bpy.context ) :
        return context.mode == "OBJECT"

    def invoke( self, context: bpy.context, _ ) :
        if not self.filepath :
            self.filepath = ".Block.Gbx"

        context.window_manager.fileselect_add( self )
        return { "RUNNING_MODAL" }

    def execute( self, context: bpy.context ) :
        gbx = GbxArchive( CLASS_ID )
        gbx.context[ "depsgraph" ] = context.evaluated_depsgraph_get()

        try :
            if not self.block_id :
                raise Exception( "Block ID is empty" )

            if not self.block_author :
                raise Exception( "Block author is empty" )

            root_object_kind = self.root_object_kind

            if root_object_kind == "SceneCollection" :
                root_object = context.scene.collection
            elif root_object_kind == "SelectedCollection" :
                root_object = context.collection
            elif root_object_kind == "SelectedObject" :
                root_object = context.object

                if root_object is None :
                    raise Exception( "No object is selected" )
            else :
                raise Exception( "Unknown root object kind \"{0}\"".format( root_object_kind ) )

            unlimiter_block(
                gbx,
                self.block_id,
                self.block_author,
                self.spawn_point,
                root_object,
            )
        except Exception as error :
            self.report( { "ERROR" }, str( error ) )
            print_exception( error )
            return { "CANCELLED" }

        gbx.do_save( self.properties.filepath )
        return { "FINISHED" }

def add_export( self, _ ) :
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