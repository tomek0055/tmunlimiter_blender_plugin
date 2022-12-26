from .game_materials.stadium import MATERIALS_STADIUM
from .game_materials.alpine import MATERIALS_ALPINE
from .game_materials.island import MATERIALS_ISLAND
from .game_materials.coast import MATERIALS_COAST
from .game_materials.rally import MATERIALS_RALLY
from .game_materials.speed import MATERIALS_SPEED
from .game_materials.bay import MATERIALS_BAY
from ..blender_gbx import ExternalRef
import bpy

class TMUnlimiterObjectTextureGame( bpy.types.PropertyGroup ) :

    environment: bpy.props.EnumProperty(
        name = "Environment",
        items = [
            ( "Speed", "Desert", "Desert (Speed) environment" ),
            ( "Rally", "Rally", "Rally environment" ),
            ( "Alpine", "Snow", "Snow (Alpine) environment" ),
            ( "Island", "Island", "Island environment" ),
            ( "Coast", "Coast", "Coast environment" ),
            ( "Bay", "Bay", "Bay environment" ),
            ( "Stadium", "Stadium", "Stadium environment" ),
        ],
        default = "Stadium",
    )

    def get_environment_materials( self, context ) :
        if self.environment == "Speed" :
            return MATERIALS_SPEED
        elif self.environment == "Rally" :
            return MATERIALS_RALLY
        elif self.environment == "Alpine" :
            return MATERIALS_ALPINE
        elif self.environment == "Island" :
            return MATERIALS_ISLAND
        elif self.environment == "Coast" :
            return MATERIALS_COAST
        elif self.environment == "Bay" :
            return MATERIALS_BAY
        elif self.environment == "Stadium" :
            return MATERIALS_STADIUM
        else :
            raise "Unknown environment \"{0}\"".format( self.environment )

    def get_material_path( self ) :
        return (
            ( self.environment, "Media", "Material" ),
            ExternalRef( self.game_material )
        )

    game_material: bpy.props.EnumProperty(
        name = "Game material",
        items = get_environment_materials,
    )