from .blender_gbx import BlenderGbx
from .plug_solid import plug_solid
import bpy

CLASS_ID = 0x3F004000

def unlimiter_block_v1(
    gbx : BlenderGbx,
    block_id : str,
    block_author : str,
    spawn_point : list[ float ],
    root : bpy.types.Object
) :
    gbx.nat32( CLASS_ID )
    # spawn point
    gbx.real( spawn_point[ 0 ] )
    gbx.real( spawn_point[ 1 ] )
    gbx.real( spawn_point[ 2 ] )
    # block id
    gbx.string( block_id )
    # block author
    gbx.string( block_author )
    # unlimiter material definitions - not supported by this exporter
    gbx.nat32( 0 )
    # solid
    plug_solid( gbx, root )
    # normally 0xfacade01 should be written here
    # but unlimiter custom block archive function
    # have custom logic, and does not inherit original game logic
    # gbx.nat32( 0xFACADE01 )