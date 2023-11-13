from io import BytesIO
from datetime import datetime, timezone
from .blender_gbx import GbxArchive, HeaderChunk
from .plug_tree import plug_tree_from_object

from .variation import TMUnlimiter_Variation
from .variants import TMUnlimiter_Variants

import bpy

class TMUnlimiter_BlockDefinition( bpy.types.PropertyGroup ) :
    __BLOCK_TYPES__ = [
        ( "classic", "Classic", "Classic block type" ),
        ( "road", "Road", "Road block type" )
    ]

    __WAYPOINT_TYPES__ = [
        ( "none", "None", "Block does not act as a waypoint" ),
        ( "start", "Start", "Block is a start" ),
        ( "checkpoint", "Checkpoint", "Block is a checkpoint" ),
        ( "finish", "Finish", "Block is a finish" ),
        ( "multilap", "Multilap", "Block is a multilap (acts both as a start and finish)" ),
    ]

    def get_available_variants( self, __context__: bpy.context ) :
        if self.block_type == "classic" :
            return [
                ( "default", "Default", "Default variant" )
            ]
        elif self.block_type == "road" :
            return [
                ( "piece", "Single piece", "Single road piece, not connected to any road or block" ),
                ( "deadend", "Deadend", "Deadend" ),
                ( "turn", "Turn", "Turn" ),
                ( "straight", "Straight", "Straight" ),
                ( "t_junction", "T-Junction", "T-Junction" ),
                ( "cross_junction", "Cross junction", "Cross junction" ),
            ]
        else :
            raise Exception( f'Unknown block type "{ self.block_type }"' )

    def get_selected_variants( self ) -> TMUnlimiter_Variants :
        return self.path_resolve( f"variants_{ self.block_type }_{ self.selected_variant }" )

    def get_selected_variations( self, selected_variant: TMUnlimiter_Variants = None ) -> bpy.types.bpy_prop_collection :
        if not selected_variant :
            selected_variant = self.get_selected_variants()

        return selected_variant.path_resolve( f"{ self.selected_variant_type }_variations" )

    def get_selected_variation( self, selected_variants = None, selected_variations = None ) -> TMUnlimiter_Variation | None :
        if not selected_variants :
            selected_variants = self.get_selected_variants()

        if not selected_variations :
            selected_variations = self.get_selected_variations( selected_variants )

        if selected_variants.selected_variation_index < len( selected_variations ) :
            return selected_variations[ selected_variants.selected_variation_index ]

        return None

    def is_trigger_allowed( self ) :
        return self.waypoint_type in { "checkpoint", "finish", "multilap" }

    def validate_identifier( self ) :
        if not self.identifier :
            return ( False, "Block identifier is empty" )

        is_checkpoint = self.identifier.find( "Checkpoint" ) != -1 or self.identifier.find( "CheckPoint" ) != -1

        if self.waypoint_type != "checkpoint" and is_checkpoint :
            return ( False, 'Block identifier cannot contain "Checkpoint" or "CheckPoint" word' )

        if self.waypoint_type == "checkpoint" and not is_checkpoint :
            return ( False, 'Block identifier must contain "Checkpoint" or "CheckPoint" word' )

        return ( True, None )

    def validate_author( self ) :
        if not self.author :
            return ( False, "Block author field is empty" )

        if self.author == "Nadeo" :
            return ( False, 'Block author cannot be "Nadeo"' )

        return ( True, None )

    def __validate_variation__( self, variant: TMUnlimiter_Variation ) :
        if not self.is_trigger_allowed() :
            return ( True, None )

        validation_result = variant.validate_model()

        if not validation_result[ 0 ] :
            return validation_result

        return variant.validate_trigger()

    def validate_variants( self ) :
        available_variants = self.get_available_variants( None )

        for variant_id, variant_title, __variant_description__ in available_variants :
            variants = self.path_resolve( f"variants_{ self.block_type }_{ variant_id }" )

            if len( variants.ground_variations ) > 64 :
                return ( False, f'Variant "{ variant_title }" exceeds maximum number of ground variations (64)' )
            
            for ground_variation in variants.ground_variations :
                validation_result = self.__validate_variation__( ground_variation )

                if not validation_result[ 0 ] :
                    return validation_result

            if len( variants.air_variations ) > 64 :
                return ( False, f'Variant "{ variant_title }" exceeds maximum number of air variations (64)' )

            for air_variation in variants.air_variations :
                validation_result = self.__validate_variation__( air_variation )

                if not validation_result[ 0 ] :
                    return validation_result

        return ( True, None )

    def archive( self, gbx: GbxArchive ) :
        if "depsgraph" not in gbx.context :
            raise Exception( "Evaluted depsgraph is required to archive block definition" )

        validation_result, validation_message = self.validate_identifier()

        if not validation_result :
            raise Exception( validation_message )

        validation_result, validation_message = self.validate_author()

        if not validation_result :
            raise Exception( validation_message )

        validation_result, validation_message = self.validate_variants()

        if not validation_result :
            raise Exception( validation_message )

        header_chunk = HeaderChunk( 0x3f002000 )
        header_chunk.mw_id( self.identifier )
        header_chunk.mw_id( self.author )
        header_chunk.nat64( int( datetime.now( timezone.utc ).timestamp() * 1000 ) )
        gbx.header_chunk( header_chunk )

        gbx.context[ "objects_data" ] = {}
        gbx.context[ "archived_objects" ] = set()
        gbx.context[ "replacement_textures" ] = {}
        gbx.context[ "custom_texture_references" ] = {}

        # Archive variant models to the independent buffers
        def archive_object( object: bpy.types.Object ) :
            if not object :
                return

            if object in gbx.context[ "objects_data" ] :
                return

            primary_buffer = gbx.attach_buffer( BytesIO() )
            _, _, instance_index = gbx.mw_ref( plug_tree_from_object, object )
            plug_tree_buffer = gbx.attach_buffer( primary_buffer )

            gbx.context[ "objects_data" ][ object ] = ( instance_index, plug_tree_buffer )

        def archive_variation( variation: TMUnlimiter_Variation ) :
            archive_object( variation.model )

            if self.is_trigger_allowed() :
                archive_object( variation.trigger )

        available_variants = self.get_available_variants()

        for variant_id, __variant_title__, __variant_description__ in available_variants :
            variants = self.path_resolve( f"variants_{ self.block_type }_{ variant_id }" )

            for ground_variation in variants.ground_variations :
                archive_variation( ground_variation )

            for air_variation in variants.air_variations :
                archive_variation( air_variation )

        # Replacement texture archivization
        replacement_texture_flags = 0
        replacement_texture_instance_indices = []

        for replacement_texture_type in range( 0, 4 ) :
            if not replacement_texture_type in gbx.context[ "replacement_textures" ] :
                continue

            replacement_texture_flags = replacement_texture_flags | 1 << replacement_texture_type
            replacement_texture_instance_indices.append( gbx.context[ "replacement_textures" ][ replacement_texture_type ] )

        gbx.nat8( replacement_texture_flags )

        for replacement_texture_instance_index in replacement_texture_instance_indices :
            gbx.nat32( replacement_texture_instance_index )

        # User texture archivization
        custom_texture_references = gbx.context[ "custom_texture_references" ]
        gbx.nat32( len( custom_texture_references ) )

        for custom_texture_tuple in custom_texture_references :
            gbx.nat32( custom_texture_references[ custom_texture_tuple ] )

            gbx.string( custom_texture_tuple[ 0 ] ) # texture.filepath
            gbx.nat8( int( custom_texture_tuple[ 1 ] ) ) # texture.filtering
            gbx.nat8( int( custom_texture_tuple[ 2 ] ) ) # texture.addressing

        # Block type archivization
        if self.block_type == "classic" :
            gbx.nat8( 2 )
        elif self.block_type == "road" :
            gbx.nat8( 3 )
        else :
            raise Exception( f'Unknown block type "{ self.block_type }"' )

        # Waypoint type archivization
        if self.waypoint_type == "start" :
            gbx.nat8( 0 )
        elif self.waypoint_type == "finish" :
            gbx.nat8( 1 )
        elif self.waypoint_type == "checkpoint" :
            gbx.nat8( 2 )
        elif self.waypoint_type == "none" :
            gbx.nat8( 3 )
        elif self.waypoint_type == "multilap" :
            gbx.nat8( 4 )
        else :
            raise Exception( f'Unknown waypoint type "{ self.waypoint_type }"' )

        # Write variations previously archived to the independent buffers
        def archive_variation_from_gbx_context( object: bpy.types.Object ) :
            if not object or not object in gbx.context[ "objects_data" ] :
                gbx.nat32( -1 )
                return

            instance_index, plug_tree_data = gbx.context[ "object_data" ][ object ]

            gbx.nat32( instance_index )

            if not object in gbx.context[ "archived_objects" ] :
                gbx.context[ "archived_objects" ].add( object )
                gbx.data( plug_tree_data )

        def archive_variations_from_gbx_context( variations ) :
            gbx.nat32( len( variations ) )

            for variation in variations :
                archive_variation_from_gbx_context( variation.model )

                if self.is_trigger_allowed() :
                    archive_variation_from_gbx_context( variation.trigger )

        for variant_id, __variant_title__, __variant_description__ in available_variants :
            variants = self.path_resolve( f"variants_{ self.block_type }_{ variant_id }" )

            archive_variations_from_gbx_context( variants.ground_variations )
            archive_variations_from_gbx_context( variants.air_variations )

        # Spawn location
        def write_spawn_location( object: bpy.types.Object ) :
            if not object :
                gbx.real( 0 )
                gbx.real( 0 )
                gbx.real( 0 )
                gbx.real( 0 )
                gbx.real( 0 )
                gbx.real( 0 )
            else :
                gbx.real( object.location.x )
                gbx.real( object.location.z )
                gbx.real( -object.location.y )
                gbx.real( object.rotation_euler.x )
                gbx.real( object.rotation_euler.z )
                gbx.real( -object.rotation_euler.y )

        write_spawn_location( self.ground_spawn_location_object )
        write_spawn_location( self.air_spawn_location_object )

        gbx.real( self.air_spawn_location.x )
        gbx.real( self.air_spawn_location.y )
        gbx.real( self.air_spawn_location.z )
        gbx.real( self.air_spawn_rotation.x )
        gbx.real( self.air_spawn_rotation.y )
        gbx.real( self.air_spawn_rotation.z )

    identifier: bpy.props.StringProperty( name = "Identifier" )
    author: bpy.props.StringProperty( name = "Author" )
    block_type: bpy.props.EnumProperty( items = __BLOCK_TYPES__, name = "Block Type" )
    waypoint_type: bpy.props.EnumProperty( items = __WAYPOINT_TYPES__, name = "Waypoint Type", default = "none" )

    selected_variant: bpy.props.EnumProperty( items = get_available_variants, name = "Selected variant", options = { "SKIP_SAVE" } )
    selected_variant_type: bpy.props.EnumProperty( items = [ ( "ground", "Ground", "Ground variant type" ), ( "air", "Air", "Air variant type" ) ], name = "Selected variant type", options = { "SKIP_SAVE" } )

    variants_classic_default: bpy.props.PointerProperty( type = TMUnlimiter_Variants )
    variants_road_piece: bpy.props.PointerProperty( type = TMUnlimiter_Variants )
    variants_road_deadend: bpy.props.PointerProperty( type = TMUnlimiter_Variants )
    variants_road_turn: bpy.props.PointerProperty( type = TMUnlimiter_Variants )
    variants_road_straight: bpy.props.PointerProperty( type = TMUnlimiter_Variants )
    variants_road_t_junction: bpy.props.PointerProperty( type = TMUnlimiter_Variants )
    variants_road_cross_junction: bpy.props.PointerProperty( type = TMUnlimiter_Variants )

    def poll_suitable_location_object( self, object: bpy.types.Object ) :
        return object.type == "EMPTY"

    ground_spawn_location_object: bpy.props.PointerProperty( name = "Ground spawn location", type = bpy.types.Object, poll = poll_suitable_location_object )
    air_spawn_location_object: bpy.props.PointerProperty( name = "Air spawn location", type = bpy.types.Object, poll = poll_suitable_location_object )