from .blender_gbx import HeaderChunk, GbxArchive
from datetime import datetime, timezone
from .plug_solid import plug_solid
from io import BytesIO
import bpy

VERSION = 0
CLASS_ID = 0x3f002000

def unlimiter_block(
    gbx: GbxArchive,
    block_id: str,
    block_author: str,
    spawn_point: list[float],
    root: bpy.types.Collection | bpy.types.Object
) :
    header_chunk = HeaderChunk( CLASS_ID )
    header_chunk.mw_id( block_id )
    header_chunk.mw_id( block_author )
    header_chunk.nat64( int( datetime.now( timezone.utc ).timestamp() * 1000 ) )
    gbx.header_chunk( header_chunk )

    if "replacement_textures" not in gbx.context :
        gbx.context[ "replacement_textures" ] = {}

    if "custom_texture_references" not in gbx.context :
        gbx.context[ "custom_texture_references" ] = {}

    # solid
    plug_solid( gbx, root )
    solid_data = gbx.attach_buffer( BytesIO() )

    # replacement textures
    replacement_textures = gbx.context[ "replacement_textures" ]
    gbx.nat32( len( replacement_textures ) )

    for replacement_texture_type in replacement_textures :
        gbx.nat32( replacement_textures[ replacement_texture_type ] )
        gbx.nat32( int( replacement_texture_type ) )

    # unlimiter custom texture references
    custom_texture_references = gbx.context[ "custom_texture_references" ]
    gbx.nat32( len( custom_texture_references ) )

    for custom_texture_tuple in custom_texture_references :
        gbx.nat32( custom_texture_references[ custom_texture_tuple ] )
        
        gbx.string( custom_texture_tuple[ 0 ] ) # texture.filepath
        gbx.nat32( int( custom_texture_tuple[ 1 ] ) ) # texture.filtering
        gbx.nat32( int( custom_texture_tuple[ 2 ] ) ) # texture.addressing

    gbx.data( solid_data )
    gbx.real( spawn_point[ 0 ] )
    gbx.real( spawn_point[ 1 ] )
    gbx.real( spawn_point[ 2 ] )
    block_data = gbx.attach_buffer( BytesIO() )

    gbx.nat32( CLASS_ID + VERSION )
    gbx.nat32( 0x534b4950 )
    gbx.nat32( block_data.tell() )
    gbx.data( block_data )
    gbx.nat32( 0xfacade01 )