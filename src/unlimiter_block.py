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
    root: bpy.types.Collection
) :
    header_chunk = HeaderChunk( CLASS_ID )
    header_chunk.nat8( VERSION )
    header_chunk.mw_id( block_id )
    header_chunk.mw_id( block_author )
    header_chunk.nat64( int( datetime.now( timezone.utc ).timestamp() * 1000 ) )
    gbx.header_chunk( header_chunk )

    gbx.nat32( CLASS_ID )
    gbx.nat8( VERSION )

    if "custom_texture_refs" not in gbx.context :
        gbx.context[ "custom_texture_refs" ] = {}

    new_body = BytesIO()

    # solid
    old_body = gbx.attach_buffer( new_body )
    plug_solid( gbx, root )
    gbx.attach_buffer( old_body )

    # unlimiter custom texture references
    custom_texture_references = gbx.context[ "custom_texture_refs" ]
    gbx.nat32( len( custom_texture_references ) )

    for instance_idx, path in custom_texture_references.values() :
        gbx.nat32( instance_idx )
        gbx.string( path )
        gbx.nat32( 0 ) # adressing
        gbx.nat32( 0 ) # filtering

    gbx.data( new_body )
    gbx.mw_id( block_id )
    gbx.mw_id( block_author )
    gbx.real( spawn_point[ 0 ] )
    gbx.real( spawn_point[ 1 ] )
    gbx.real( spawn_point[ 2 ] )
    gbx.nat32( 0xFACADE01 )