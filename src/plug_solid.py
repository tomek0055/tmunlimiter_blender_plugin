from .plug_tree import plug_tree_from_object
from .blender_gbx import GbxArchive
import bpy

def plug_solid( gbx: GbxArchive, root: bpy.types.Object ) :
# 0x09005011 -- start
    gbx.nat32( 0x09005011 )
    gbx.nat32( 0x00000000 )
    gbx.nat32( 0x00000000 )

    if type( root ) is bpy.types.Object :
        gbx.mw_ref( plug_tree_from_object, root )
    else :
        gbx.nat32( 0xffffffff )
# 0x09005011 -- end
    gbx.nat32( 0xfacade01 )
# 0x09005000 -- end