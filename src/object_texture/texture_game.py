from __future__ import annotations

from .game_materials.stadium import MATERIALS_STADIUM
from .game_materials.alpine import MATERIALS_ALPINE
from .game_materials.island import MATERIALS_ISLAND
from .game_materials.coast import MATERIALS_COAST
from .game_materials.rally import MATERIALS_RALLY
from .game_materials.speed import MATERIALS_SPEED
from .game_materials.bay import MATERIALS_BAY
from ..blender_gbx import GbxArchive, ExternalRef
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

    def get_environment_materials( self ) :
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
            raise Exception( "Unknown environment \"{0}\"".format( self.environment ) )

    def get_selected_environment_material( self ) :
        environment_materials = self.get_environment_materials()

        for environment_material in environment_materials :
            if environment_material[ 0 ] == self.game_material :
                return ( True, environment_material )

        return ( False, None )

    def get_prepared_environment_materials_enum( self, _ ) :
        environment_materials = self.get_environment_materials()
        result = []

        for environment_material in environment_materials :
            result.append( ( environment_material[ 0 ], environment_material[ 0 ][ : -13 ], "" ) )

        return result

    game_material: bpy.props.EnumProperty(
        name = "Game material",
        items = get_prepared_environment_materials_enum,
    )

    def copy_from( self, texture_game: TMUnlimiterObjectTextureGame ) :
        self.environment = texture_game.environment
        self.game_material = texture_game.game_material

    def archive( self, gbx: GbxArchive ) :
        gbx.external_ref( ( self.environment, "Media", "Material" ), ExternalRef( self.game_material ) )