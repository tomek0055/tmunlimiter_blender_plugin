from io import BytesIO
from datetime import datetime, timezone
from .blender_gbx import GbxArchive, HeaderChunk
from .plug_tree import plug_tree_from_object

from .block_unit import TMUnlimiter_BlockUnit
from .variation import TMUnlimiter_Variation, poll_object
from .variants import TMUnlimiter_Variants

import typing
import bpy

class TMUnlimiter_BlockDefinition( bpy.types.PropertyGroup ) :
    __BLOCK_TYPES__ = \
    [
        ( "classic", "Classic", "Classic block type" ),
        ( "road", "Road", "Road block type" )
    ]

    __WAYPOINT_TYPES__ = \
    [
        ( "none", "None", "Block does not act as a waypoint" ),
        ( "start", "Start", "Block is a start" ),
        ( "checkpoint", "Checkpoint", "Block is a checkpoint" ),
        ( "finish", "Finish", "Block is a finish" ),
        ( "multilap", "Multilap", "Block is a multilap (acts both as a start and finish)" ),
    ]

    def get_available_variants( self, __context__: bpy.context ) :
        if self.block_type == "classic" :
            return \
            [
                ( "default", "Default", "Default variant" )
            ]
        elif self.block_type == "road" :
            return \
            [
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

        if selected_variants.selected_variation_index >= 0 and selected_variants.selected_variation_index < len( selected_variations ) :
            return selected_variations[ selected_variants.selected_variation_index ]

        return None

    def get_selected_block_units( self ) -> bpy.types.bpy_prop_collection :
        return self.path_resolve( f"{ self.selected_block_unit_type }_block_units" )

    def get_selected_block_unit( self, block_units = None ) -> TMUnlimiter_BlockUnit | None :
        if not block_units :
            block_units = self.get_selected_block_units()

        if self.selected_block_unit_index >= 0 and self.selected_block_unit_index < len( block_units ) :
            return block_units[ self.selected_block_unit_index ]

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

        if self.author == "Nadeo" or self.author == "nadeo" :
            return ( False, 'Block author cannot be "Nadeo" or "nadeo"' )

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

    def validate_icon( self, **kwargs ) :
        icon_to_evaluate = self.icon

        if "icon_to_evaluate" in kwargs :
            icon_to_evaluate = kwargs[ "icon_to_evaluate" ]

            if type( icon_to_evaluate ) != bpy.types.ImageTexture :
                return ( False, "Icon is not an image texture" )

        if not icon_to_evaluate :
            return ( True, None )

        if icon_to_evaluate.type != "IMAGE" :
            return ( False, 'Icon is not "IMAGE" type' )

        image = icon_to_evaluate.image

        if not image :
            return ( False, 'Texture does not have an image' )

        if len( image.size ) != 2 :
            return ( False, "Icon does not have exactly two dimensions" )

        width, height = image.size

        if width <= 0 or height <= 0 :
            return ( False, "Image is not loaded" )

        if width > 255 :
            return ( False, "Icon width exceeds maximum possible size of 255 pixels" )

        if height > 255 :
            return ( False, "Icon height exceeds maximum possible size of 255 pixels" )

        return ( True, None )

    def __validate_block_units__( self, block_units: typing.List[TMUnlimiter_BlockUnit] ) :
        for block_unit_index, block_unit in enumerate( block_units ) :
            validation_result = block_unit.validate()

            if not validation_result[ 0 ] :
                return validation_result

            if block_unit_index < 1 :
                continue

            block_unit_offset = block_unit.calculate_offset()
            back_block_unit_index = block_unit_index

            while back_block_unit_index :
                back_block_unit_index = back_block_unit_index - 1
                back_block_unit = block_units[ back_block_unit_index ]
                back_block_unit_offset = back_block_unit.calculate_offset()

                if block_unit_offset == back_block_unit_offset :
                    return ( False, f"Block Unit #{ 1 + back_block_unit_index } has the same coordinates" )

        return ( True, None )

    def validate_block_units( self ) :
        validation_result = self.__validate_block_units__( self.ground_block_units )

        if not validation_result[ 0 ] :
            return validation_result

        return self.__validate_block_units__( self.air_block_units )

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

        validation_result, validation_message = self.validate_icon()

        if not validation_result :
            raise Exception( validation_message )

        validation_result, validation_message = self.validate_block_units()

        if not validation_result :
            raise Exception( validation_message )

        header_chunk = HeaderChunk( 0x3f_002_002 )
        header_chunk.mw_id( self.identifier )
        header_chunk.mw_id( self.author )
        flags = 0

        if self.backward_compatibility_enabled :
            flags = 1

        # Block type archivization
        if self.block_type == "classic" :
            flags |= 2 << 1
        elif self.block_type == "road" :
            flags |= 3 << 1
        else :
            raise Exception( f'Unknown block type "{ self.block_type }"' )

        # Waypoint type archivization
        if self.waypoint_type == "start" :
            pass
        elif self.waypoint_type == "finish" :
            flags |= 1 << 4
        elif self.waypoint_type == "checkpoint" :
            flags |= 2 << 4
        elif self.waypoint_type == "none" :
            flags |= 3 << 4
        elif self.waypoint_type == "multilap" :
            flags |= 4 << 4
        else :
            raise Exception( f'Unknown waypoint type "{ self.waypoint_type }"' )

        if self.icon :
            flags |= 1 << 7

        header_chunk.nat8( flags )

        if self.icon :
            image: bpy.types.Image = self.icon.image

            header_chunk.nat8( image.size[ 0 ] ) # Width
            header_chunk.nat8( image.size[ 1 ] ) # Height

            for pixel_index in range( image.size[ 0 ] * image.size[ 1 ] ) :
                component_index = pixel_index * 4

                header_chunk.nat8( int( image.pixels[ component_index + 2 ] * 255 ) )
                header_chunk.nat8( int( image.pixels[ component_index + 1 ] * 255 ) )
                header_chunk.nat8( int( image.pixels[ component_index + 0 ] * 255 ) )
                header_chunk.nat8( int( image.pixels[ component_index + 3 ] * 255 ) )

        header_chunk.nat64( int( datetime.now( timezone.utc ).timestamp() * 1000 ) )
        gbx.header_chunk( header_chunk )

        gbx.context[ "objects_data" ] = {}
        gbx.context[ "archived_objects" ] = set()
        gbx.context[ "replacement_textures" ] = {}
        gbx.context[ "custom_texture_references" ] = {}
        root_buffer = gbx.attach_buffer( BytesIO() )

        # Archive variant models to the independent buffers
        def archive_object( object: bpy.types.Object ) :
            if not object :
                return

            if object in gbx.context[ "objects_data" ] :
                return

            instance_index = gbx.add_instance( write = False )
            primary_buffer = gbx.attach_buffer( BytesIO() )
            plug_tree_from_object( gbx, object )

            gbx.context[ "objects_data" ][ object ] = ( instance_index, gbx.attach_buffer( primary_buffer ) )

        def archive_variation( variation: TMUnlimiter_Variation ) :
            archive_object( variation.model )

            if self.is_trigger_allowed() :
                archive_object( variation.trigger )

        available_variants = self.get_available_variants( None )

        for variant_id, __variant_title__, __variant_description__ in available_variants :
            variants = self.path_resolve( f"variants_{ self.block_type }_{ variant_id }" )

            for ground_variation in variants.ground_variations :
                archive_variation( ground_variation )

            for air_variation in variants.air_variations :
                archive_variation( air_variation )

        if self.backward_compatibility_enabled :
            archive_object( self.backward_compatibility_model )

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

        # Write variations previously archived to the independent buffers
        def archive_variation_from_gbx_context( object: bpy.types.Object ) :
            if not object :
                gbx.nat32( -1 )
                return

            instance_index, plug_tree_data = gbx.context[ "objects_data" ][ object ]
            gbx.nat32( instance_index )

            if not object in gbx.context[ "archived_objects" ] :
                gbx.context[ "archived_objects" ].add( object )
                gbx.data( plug_tree_data )

        def archive_variations_from_gbx_context( variations ) :
            gbx.nat8( len( variations ) )

            for variation in variations :
                archive_variation_from_gbx_context( variation.model )

                if self.is_trigger_allowed() :
                    archive_variation_from_gbx_context( variation.trigger )

                gbx.nat8( variation.pre_light_gen_tile_count )

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
                gbx.real( object.location.y )
                gbx.real( object.location.z )
                gbx.real( object.location.x )
                gbx.real( object.rotation_euler.y )
                gbx.real( object.rotation_euler.z )
                gbx.real( object.rotation_euler.x )

        write_spawn_location( self.ground_spawn_location_object )
        write_spawn_location( self.air_spawn_location_object )

        # Block units
        gbx.nat32( len( self.ground_block_units ) )
        gbx.nat32( len( self.air_block_units ) )

        for ground_block_unit in self.ground_block_units :
            ground_block_unit.archive( gbx )

        for air_block_unit in self.air_block_units :
            air_block_unit.archive( gbx )

        if self.backward_compatibility_enabled :
            archive_variation_from_gbx_context( self.backward_compatibility_model )

        # Finalize archivization
        chunk_buffer = gbx.attach_buffer( root_buffer ).getvalue()

        gbx.nat32( 0x3f002002 )
        gbx.nat32( 0x534b4950 )
        gbx.nat32( len( chunk_buffer ) )
        gbx.data( chunk_buffer )
        gbx.nat32( 0xfacade01 )

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

    backward_compatibility_enabled: bpy.props.BoolProperty( name = "Is backward compatible", default = False )
    backward_compatibility_model: bpy.props.PointerProperty( name = "Backward compatible model", type = bpy.types.Object, poll = poll_object )

    def __validate_icon__( self, texture: bpy.types.ImageTexture ) :
        return self.validate_icon( icon_to_evaluate = texture )[ 0 ]

    icon: bpy.props.PointerProperty( name = "Icon", type = bpy.types.Texture, poll = __validate_icon__ )

    selected_block_unit_index: bpy.props.IntProperty( options = { "HIDDEN", "SKIP_SAVE" } )
    selected_block_unit_type: bpy.props.EnumProperty( items = [ ( "ground", "Ground", "Ground block unit type" ), ( "air", "Air", "Air block unit type" ) ], name = "Selected block unit type", options = { "SKIP_SAVE" } )
    ground_block_units: bpy.props.CollectionProperty( type = TMUnlimiter_BlockUnit )
    air_block_units: bpy.props.CollectionProperty( type = TMUnlimiter_BlockUnit )