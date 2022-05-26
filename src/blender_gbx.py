from io import BytesIO
import struct
import lzo
import bpy

from .validators import (
    validate_plug_surface,
    validate_plug_visual_3d,
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
    data.write( value.encode( "utf_16_le" if is_wide else "utf_8" ) )

def string( data : BytesIO, value : str, is_wide : bool = False ) :
    nat32( data, len( value ) )
    text( data, value, is_wide )

class BlenderGbx :

    def __init__(
        self,
        class_id : int,
        depsgraph : bpy.types.Depsgraph,
        validators : dict = {}
    ) :
        self.mw_ids = []
        self.mw_id_used = False

        self.body = BytesIO()

        self.class_id = class_id
        self.depsgraph = depsgraph
        self.instances = 0

        self.external_refs = []

        self.validators = {
            "plug_surface" : validate_plug_surface,
            **validators,
            "plug_visual_3d" : validate_plug_visual_3d,
        }

    def nat8( self, value : int ) :
        nat8( self.body, value )

    def nat16( self, value : int ) :
        nat16( self.body, value )

    def nat32( self, value : int ) :
        nat32( self.body, value )

    def real( self, value : float ) :
        real( self.body, value )

    def string( self, value : str, is_wide = False ) :
        string( self.body, value, is_wide )

    def external_ref( self, path : list[ str ], file_name : str, use_fid : bool = False ) :
        self.instances += 1

        self.external_refs.append( {
            "path" : path,
            "use_fid" : use_fid,
            "file_name" : file_name,
            "instance_idx" : self.instances,
        } )

        self.nat32( self.instances )

    def mw_id( self, mw_id : str = "" ) :
        if not self.mw_id_used :
            self.mw_id_used = True
            self.nat32( 0x00000003 )

        if len( mw_id ) == 0 :
            self.nat32( 0xFFFFFFFF )
        elif mw_id in self.mw_ids :
            self.nat32( 0x40000001 + self.mw_ids.index( mw_id ) )
        else :
            self.mw_ids.append( mw_id )
            self.nat32( 0x40000000 )
            self.string( mw_id )

    def mw_ref( self, function, *function_args, **function_kwargs ) :
        valid_ref = \
            not function.__name__ in self.validators \
                or \
            self.validators[ function.__name__ ]( *function_args, **function_kwargs )

        if not valid_ref :
            self.nat32( 0xFFFFFFFF )

            return (
                valid_ref,
                None,
            )

        self.instances += 1
        self.nat32( self.instances )

        return (
            valid_ref,
            function( self, *function_args, **function_kwargs ),
        )

    def __save_folder_recursive__( self, header : BytesIO, folder_name : str, folder_data : dict ) :
        child_folders = folder_data[ "child_folders" ]

        string( header, folder_name )
        nat32( header, len( child_folders ) )

        for child_folder_name, child_folder in child_folders.items() :
            self.save_folder_recursive( header, child_folder_name, child_folder )

    def do_save( self, filepath : str ) :
        header = BytesIO()

        text( header, "GBX" )
        nat16( header, 6 )
        text( header, "BUCR" )
        nat32( header, self.class_id )
        nat32( header, 0x00000000 )
        nat32( header, self.instances + 1 )
        nat32( header, len( self.external_refs ) )

        if len( self.external_refs ) > 0 :
            # GBX files loaded from user directory have game data directory as root
            # and due to that fact, we don't need to set ancestor level
            nat32( header, 0 )

            total_folders_nb = 0

            root_folder = {
                "folder_idx" : 0,
                "child_folders" : {},
            }

            external_instances = []

            for external_ref in self.external_refs :
                parent_folder = root_folder

                for folder in external_ref[ "path" ] :
                    if folder not in parent_folder[ "child_folders" ] :
                        total_folders_nb += 1

                        parent_folder[ "child_folders" ][ folder ] = {
                            "folder_idx" : total_folders_nb,
                            "child_folders" : {},
                        }
                    
                    parent_folder = parent_folder[ "child_folders" ][ folder ]

                external_instances.append( {
                    "folder_idx" : parent_folder[ "folder_idx" ],
                    "external_ref" : external_ref,
                } )

            child_folders = root_folder[ "child_folders" ]

            nat32( header, len( child_folders ) )

            for child_folder_name, child_folder in child_folders.items() :
                self.__save_folder_recursive__( header, child_folder_name, child_folder )
            
            for external_instance in external_instances :
                folder_idx = external_instance[ "folder_idx" ]
                external_ref = external_instance[ "external_ref" ]

                nat32( header, 1 )
                string( header, external_ref[ "file_name" ] )
                
                nat32( header, external_ref[ "instance_idx" ] )
                nat32( header, int( external_ref[ "use_fid" ] ) )

                nat32( header, folder_idx )

        body = self.body.getvalue()
        nat32( header, len( body ) )
        body = lzo.compress( body, 9, False )
        nat32( header, len( body ) )
        header = header.getvalue()

        file = open( filepath, 'wb' )
        file.write( header )
        file.write( body )
        file.close()