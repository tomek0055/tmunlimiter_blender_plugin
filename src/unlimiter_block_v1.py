from .blender_gbx import HeaderChunk, GbxArchive
from .plug_solid import plug_solid
import bpy

CLASS_ID = 0x3f002000

# Work in progress
def unlimiter_block_v1(
    gbx: GbxArchive,
    block_id: str,
    block_author: str,
    spawn_point: list[float],
    root: bpy.types.Collection
) :
    test_header_chunk = HeaderChunk( 0x3f002000 )
    test_header_chunk.mw_id( block_id )
    test_header_chunk.mw_id( block_author )
    gbx.header_chunk( test_header_chunk )

    gbx.nat32( CLASS_ID )
    gbx.nat8( 0 )

    if "custom_texture_refs" not in gbx.context :
        gbx.context[ "custom_texture_refs" ] = {}

    # solid
    old_body = gbx.attach_buffer()
    plug_solid( gbx, root )
    new_body = gbx.attach_buffer( old_body )

    # unlimiter custom texture references
    custom_texture_references = gbx.context[ "custom_texture_refs" ]
    gbx.nat32( len( custom_texture_references ) )

    for instance_idx, path in custom_texture_references.values() :
        gbx.nat32( instance_idx )
        gbx.string( path )

    gbx.data( new_body )
    gbx.nat32( 0xFACADE01 )