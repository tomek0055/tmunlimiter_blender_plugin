from io import BytesIO
import struct
import bmesh
import bpy
import lzo

from bpy_extras.io_utils import (
    ExportHelper,
)

def nat8( data : BytesIO, value : int ) :
    data.write( value.to_bytes( 1, "little" ) )

def nat16( data : BytesIO, value : int ) :
    data.write( value.to_bytes( 2, "little" ) )

def nat32( data : BytesIO, value : int ) :
    data.write( value.to_bytes( 4, "little" ) )

def real( data : BytesIO, value : float ) :
    data.write( struct.pack( "f", value ) )

def text( data : BytesIO, value : str, is_wide : bool = False ) :
    data.write( value.encode( "utf_16" if is_wide else "utf_8" ) )

def string( data : BytesIO, value : str, is_wide : bool = False ) :
    nat32( data, len( value ) )
    text( data, value, is_wide )

class Gbx :

    def __init__( self, class_id : int, filepath : str ) :
        self.mw_ids = []
        self.class_id = class_id
        self.filepath = filepath
        self.instances = 0

    def mw_id( self, data : BytesIO, id : str ) :
        if len( self.mw_ids ) < 1 :
            nat32( data, 0x00000003 )

        index = 0x40000000

        if id in self.mw_ids :
            nat32( data, self.mw_ids.index( id ) + index + 1 )
        else :
            self.mw_ids.append( id )

            nat32( data, index )
            string( data, id )

    def mw_ref( self, data : BytesIO, executor ) :
        self.instances += 1
        nat32( data, self.instances )
        executor()

    def do_save( self, header : BytesIO, body : BytesIO ) :
        text( header, "GBX" )
        nat16( header, 6 )
        text( header, "BUCR" )
        nat32( header, self.class_id )
        nat32( header, 0x00000000 )
        nat32( header, self.instances + 1 )
        nat32( header, 0x00000000 )

        body = body.getvalue()
        nat32( header, len( body ) )
        body = lzo.compress( body, 9, False )
        nat32( header, len( body ) )
        header = header.getvalue()

        file = open( self.filepath, 'wb' )
        file.write( header )
        file.write( body )
        file.close()

def plug_visual_3d( data : BytesIO, object : bpy.types.Object, gbx : Gbx ) :
    mesh = bmesh.new()
    mesh.from_mesh( object.data )
    bmesh.ops.triangulate( mesh, faces = mesh.faces )

    uv_layers = mesh.loops.layers.uv.values()
    triangles = mesh.calc_loop_triangles()

    vertices_uv_tuples = [
        (
            [ {} for _ in range( len( uv_layers ) ) ],
            [ vert ]
        )
        for vert in mesh.verts
    ]

    uvs_v2 = [ {} for _ in range( len( uv_layers ) ) ]
    loops_v2 = []

    for loops in triangles :
        for loop in loops :
            vert = loop.vert

            for uv_idx, uv_layer in enumerate( uv_layers ) :
                uv_layers_tuples, vertices = vertices_uv_tuples[ vert.index ]
                uv_layer_tuples = uv_layers_tuples[ uv_idx ]
                uv_tuple = loop[ uv_layer ].uv.to_tuple()

                if not uv_tuple in uv_layer_tuples :
                    uv_layer_tuples_size = len( uv_layer_tuples )

                    if uv_layer_tuples_size < len( vertices ) :
                        vert = vertices[ uv_layer_tuples_size ]
                    else :
                        vert = mesh.verts.new( vert.co, vert )
                        vert.index = len( mesh.verts ) - 1
                        vertices.append( vert )

                    uv_layer_tuples[ uv_tuple ] = vert
                    uvs_v2[ uv_idx ][ vert.index ] = uv_tuple
                else :
                    vert = uv_layer_tuples[ uv_tuple ]

            loops_v2.append( vert.index )

    if len( mesh.verts ) > 65535 :
        raise "Object exceeds 65535 vertices"

# 09-01E-000 -- Start
    nat32( data, 0x0901E000 )
# 09-006-00E -- Start
    nat32( data, 0x0900600E )
    nat32( data, 0x00000038 )
    nat32( data, len( uv_layers ) )
    nat32( data, len( mesh.verts ) )
    nat32( data, 0x00000000 )

    for uv_idx in range( len( uv_layers ) ) :
        nat32( data, 0x00000000 )

        uvs = uvs_v2[ uv_idx ]

        for vertex_idx in range( len( mesh.verts ) ) :
            uv_tuple = uvs.get( vertex_idx )

            if uv_tuple is None :
                uv_tuple = ( 0, 0 )

            real( data, uv_tuple[ 0 ] )
            real( data, uv_tuple[ 1 ] )

    real( data, object.dimensions.x / 2 )
    real( data, object.dimensions.z / 2 )
    real( data, object.dimensions.y / 2 )
    real( data, object.dimensions.x / 2 )
    real( data, object.dimensions.z / 2 )
    real( data, object.dimensions.y / 2 )
    nat32( data, 0x00000000 )
# 09-006-00E -- End
# 09-02C-004 -- Start
    nat32( data, 0x0902C004 )

    for vert in mesh.verts :
        real( data, vert.co.x )
        real( data, vert.co.z )
        real( data, -vert.co.y )
        real( data, vert.normal.x )
        real( data, vert.normal.z )
        real( data, -vert.normal.y )
        real( data, object.color[ 0 ] )
        real( data, object.color[ 1 ] )
        real( data, object.color[ 2 ] )
        real( data, object.color[ 3 ] )

    nat32( data, 0x00000000 )
    nat32( data, 0x00000000 )
# 09-02C-004 -- End
# 09-06A-001 -- Start
    nat32( data, 0x0906A001 )
    nat32( data, 0x00000001 )
# 09-057-000 -- Start
    nat32( data, 0x09057000 )
    nat32( data, 0x00000002 )
    nat32( data, len( loops_v2 ) )

    for loop in loops_v2 :
        nat16( data, loop )

    nat32( data, 0xFACADE01 )
# 09-057-000 -- End
# 09-06A-001 -- End
    nat32( data, 0xFACADE01 )
# 09-01E-000 -- End

def plug_tree_from_collection( data : BytesIO, collection : bpy.types.Collection, gbx : Gbx ) :
    objects = list( filter( lambda object : object.parent is None, collection.all_objects ) )

# 09-04F-000 -- Start
    nat32( data, 0x0904F000 )

# 09-04F-00D -- Start
    nat32( data, 0x0904F00D )
    gbx.mw_id( data, collection.name )
    nat32( data, 0xFFFFFFFF )
# 09-04F-00D -- End

# 09-04F-006 -- Start
    if len( objects ) :
        nat32( data, 0x0904F006 )
        nat32( data, 0x0000000A )
        nat32( data, len( objects ) )

        for object in objects :
            gbx.mw_ref( data, lambda : plug_tree_from_object( data, object, gbx ) )
# 09-04F-006 -- End

    nat32( data, 0xFACADE01 )
# 09-04F-000 -- End

def plug_tree_from_object( data : BytesIO, object : bpy.types.Object, gbx : Gbx ) :
# 09-04F-000 -- Start
    nat32( data, 0x0904F000 )

# 09-04F-00D -- Start
    nat32( data, 0x0904F00D )
    gbx.mw_id( data, object.name )
    nat32( data, 0xFFFFFFFF )
# 09-04F-00D -- End

# 09-04F-006 -- Start
    if len( object.children ) :
        nat32( data, 0x0904F006 )
        nat32( data, 0x0000000A )
        nat32( data, len( object.children ) )

        for children in object.children :
            gbx.mw_ref( data, lambda : plug_tree_from_object( data, children, gbx ) )
# 09-04F-006 -- End

# 09-04F-016 -- Start
    nat32( data, 0x0904F016 )
    gbx.mw_ref( data, lambda : plug_visual_3d( data, object, gbx ) )
    nat32( data, 0xFFFFFFFF ) # MwNodRef< CPlugMaterial >
    nat32( data, 0xFFFFFFFF ) # MwNodRef< CPlugSurface >
    nat32( data, 0xFFFFFFFF ) # MwNodRef< CPlugTreeGenerator >
# 09-04F-016 -- End
    nat32( data, 0xFACADE01 )
# 09-04F-000 -- End

def export( context : bpy.types.Context, **keywords ) :
    print( keywords )

    body = BytesIO()
    header = BytesIO()

    gbx = Gbx( 0x09005000, keywords[ "filepath" ] )

    if keywords[ "use_active_collection" ] :
        collection = context.collection
    else :
        collection = context.scene.collection

# 0x09005000 -- start
    nat32( body, 0x09005000 )
    nat32( body, 0x00000001 )
# 0x09005011 -- start
    nat32( body, 0x09005011 )
    nat32( body, 0x00000000 )
    nat32( body, 0x00000000 )
    gbx.mw_ref( body, lambda : plug_tree_from_collection( body, collection, gbx ) )
# 0x09005011 -- end
    nat32( body, 0xFACADE01 )
# 0x09005000 -- end

    gbx.do_save( header, body )

class ExportSolidGbx( bpy.types.Operator, ExportHelper ):
    """Save as *.Solid.Gbx File"""

    bl_label = "Export *.Solid.Gbx file"
    bl_idname = "export_scene.gbx"
    bl_options = { "PRESET" }

    filter_glob : bpy.props.StringProperty(
        default = "*.Solid.Gbx",
        options = { "HIDDEN" },
    )

    use_active_collection : bpy.props.BoolProperty(
        name = "Active Collection",
        default = False,
        description = "Export only objects from the active collection",
    )

    filename_ext = ".Solid.Gbx"
    check_extension = False

    def execute( self, context ) :
        export( context, **self.as_keywords() )
        return { "FINISHED" }