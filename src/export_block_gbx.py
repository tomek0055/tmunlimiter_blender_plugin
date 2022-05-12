from .unlimiter_block_v1 import (
    unlimiter_block_v1,
    CLASS_ID,
)

from bpy_extras.io_utils import ExportHelper
from .blender_gbx import BlenderGbx
import bpy

class TMUnlimiterMaterial( bpy.types.PropertyGroup ) :

    TEXTURE_TYPES = [
        ( "NO_TEXTURE", "No texture", "No texture" ),
        ( "GAME_TEXTURE", "Game texture", "Game texture" ),
        ( "CUSTOM_TEXTURE", "Custom texture", "Custom texture" ),
    ]

    texture_type : bpy.props.EnumProperty(
        name = "Texture type",
        items = TEXTURE_TYPES,
    )

    texture_name : bpy.props.StringProperty(
        name = "Texture name",
    )

    COLLISION_TYPES = [
        ( "NO_COLLISION", "No collision", "No collision" ),
        ( "MESH_COLLISION", "Mesh collision", "Mesh collision" ),
    ]

    collision_type : bpy.props.EnumProperty(
        name = "Is collidable",
        items = COLLISION_TYPES,
    )

    COLLISION_MATERIALS = [
        ( "0", "#01: Concrete", "#01: Concrete" ),
        ( "1", "#02: Pavement", "#02: Pavement" ),
        ( "2", "#03: Grass", "#03: Grass" ),
        ( "3", "#04: Ice", "#04: Ice" ),
        ( "4", "#05: Metal", "#05: Metal" ),
        ( "5", "#06: Sand", "#06: Sand" ),
        ( "6", "#07: Dirt", "#07: Dirt" ),
        ( "7", "#08: Turbo", "#08: Turbo" ),
        ( "8", "#09: DirtRoad", "#09: DirtRoad" ),
        ( "9", "#10: Rubber", "#10: Rubber" ),
        ( "10", "#11: SlidingRubber", "#11: SlidingRubber" ),
        ( "11", "#12: Test", "#12: Test" ),
        ( "12", "#13: Rock", "#13: Rock" ),
        ( "13", "#14: Water", "#14: Water" ),
        ( "14", "#15: Wood", "#15: Wood" ),
        ( "15", "#16: Danger", "#16: Danger" ),
        ( "16", "#17: Asphalt", "#17: Asphalt" ),
        ( "17", "#18: WetDirtRoad", "#18: WetDirtRoad" ),
        ( "18", "#19: WetAsphalt", "#19: WetAsphalt" ),
        ( "19", "#20: WetPavement", "#20: WetPavement" ),
        ( "20", "#21: WetGrass", "#21: WetGrass" ),
        ( "21", "#22: Snow", "#22: Snow" ),
        ( "22", "#23: ResonantMetal", "#23: ResonantMetal" ),
        ( "23", "#24: GolfBall", "#24: GolfBall" ),
        ( "24", "#25: GolfWall", "#25: GolfWall" ),
        ( "25", "#26: GolfGround", "#26: GolfGround" ),
        ( "26", "#27: TurboRed", "#27: TurboRed" ),
        ( "27", "#28: Bumper", "#28: Bumper" ),
        ( "28", "#29: NotCollidable", "#29: NotCollidable" ),
        ( "29", "#30: FreeWheeling", "#30: FreeWheeling" ),
        ( "30", "#31: TurboRoulette", "#31: TurboRoulette" ),
    ]

    collision_material : bpy.props.EnumProperty(
        name = "Collision material",
        items = COLLISION_MATERIALS,
    )

class TMUnlimiterMaterialProperties( bpy.types.Panel ) :
    bl_idname = "OBJECT_PT_unlimiter_material_properties"
    bl_label = "TMUnlimiter Material Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw( self, context : bpy.types.Context ) :
        material = context.object.active_material

        if material is None :
            return

        data : TMUnlimiterMaterial = material.unlimiter_data

        self.layout.prop( data, "texture_type" )

        if data.texture_type != "NO_TEXTURE" :
            self.layout.prop( data, "texture_name" )

        self.layout.prop( data, "collision_type" )

        if data.collision_type != "NO_COLLISION" :
            self.layout.prop( data, "collision_material" )

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

    filename_ext = ".Block.Gbx"
    check_extension = False

    @classmethod
    def poll( self, context : bpy.context ) :
        return context.mode == "OBJECT"

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

def add_block_v1_gbx_export( self, context ) :
    self.layout.operator( ExportBlockGbx.bl_idname )

def __register__() :
    bpy.utils.register_class( ExportBlockGbx )
    bpy.utils.register_class( TMUnlimiterMaterial )
    bpy.utils.register_class( TMUnlimiterMaterialProperties )

    bpy.types.TOPBAR_MT_file_export.append( add_block_v1_gbx_export )

    bpy.types.Material.unlimiter_data = bpy.props.PointerProperty(
        type = TMUnlimiterMaterial
    )

def __unregister__() :
    bpy.types.TOPBAR_MT_file_export.remove( add_block_v1_gbx_export )
    bpy.utils.unregister_class( TMUnlimiterMaterialProperties )
    bpy.utils.unregister_class( TMUnlimiterMaterial )
    bpy.utils.unregister_class( ExportBlockGbx )