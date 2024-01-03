from typing import Any, Callable
from io import BytesIO
import struct
import lzo

def nat8( data: BytesIO, value: int ) :
    data.write( value.to_bytes( 1, "little" ) )

def nat16( data: BytesIO, value: int ) :
    data.write( value.to_bytes( 2, "little" ) )

def nat32( data: BytesIO, value: int ) :
    data.write( value.to_bytes( 4, "little" ) )

def nat64( data: BytesIO, value: int ) :
    data.write( value.to_bytes( 8, "little" ) )

def real( data: BytesIO, value: float ) :
    data.write( struct.pack( "f", value ) )

def data( data: BytesIO, value: bytes | BytesIO ) :
    if type( value ) is bytes :
        data.write( value )
    elif type( value ) is BytesIO :
        data.write( value.getvalue() )

def text( data: BytesIO, value: str, is_wide = False ) :
    data.write( value.encode( "utf_16_le" if is_wide else "utf_8" ) )

def string( data: BytesIO, value: str, is_wide = False ) :
    nat32( data, len( value ) )
    text( data, value, is_wide )

class GbxContainer :

    def __init__( self ) :
        self.mw_ids = None
        self.buffer = BytesIO()
        self.context = {}

    def nat8( self, value: int ) :
        nat8( self.buffer, value )

    def nat16( self, value: int ) :
        nat16( self.buffer, value )

    def nat32( self, value: int ) :
        nat32( self.buffer, value )

    def nat64( self, value: int ) :
        nat64( self.buffer, value )

    def real( self, value: float ) :
        real( self.buffer, value )

    def string( self, value: str, is_wide = False ) :
        string( self.buffer, value, is_wide )

    def data( self, value: BytesIO ) :
        data( self.buffer, value )

    def mw_id( self, mw_id = "" ) :
        if self.mw_ids is None :
            self.mw_ids = []
            self.nat32( 0x00000003 )

        if len( mw_id ) == 0 :
            self.nat32( 0xFFFFFFFF )
        elif mw_id in self.mw_ids :
            self.nat32( 0x40000001 + self.mw_ids.index( mw_id ) )
        else :
            self.mw_ids.append( mw_id )
            self.nat32( 0x40000000 )
            self.string( mw_id )

    def attach_buffer( self, new_buffer: BytesIO ) -> BytesIO :
        detached_buffer = self.buffer
        self.buffer = new_buffer

        return detached_buffer

class HeaderChunk( GbxContainer ) :

    def __init__( self, header_chunk_id: int, is_heavy = False ) :
        GbxContainer.__init__( self )

        self.is_heavy = is_heavy
        self.header_chunk_id = header_chunk_id

class FolderRef :

    def __init__( self ) :
        self.subfolders: dict[str, FolderRef] = {}

    def to_list( self, folders: list ) :
        folders.append( self )

        for subfolder_name in self.subfolders :
            self.subfolders[ subfolder_name ].to_list( folders )

    def archive( self, buffer: BytesIO, folder_name: str | None ) :
        if folder_name :
            string( buffer, folder_name )

        nat32( buffer, len( self.subfolders ) )

        for subfolder_name in self.subfolders :
            self.subfolders[ subfolder_name ].archive( buffer, subfolder_name )

class ExternalRef :

    def __init__( self, use_fid = False ) :
        self.use_fid = int( use_fid )

    def find_or_add_folder( self, root_folder: FolderRef ) -> FolderRef :
        return root_folder

    def archive( self, buffer: BytesIO, instance_index: int, folder_index: int ) :
        raise Exception( "Not implemented" )

class FileExternalRef( ExternalRef ) :

    def __init__( self, file_path: str | list[str] | tuple[str], use_fid = False ) :
        if len( file_path ) < 1 :
            raise Exception( "File path is empty" )

        ExternalRef.__init__( self, use_fid )

        if type( file_path ) is str :
            self.file_name = file_path
            self.file_path = tuple()
        else :
            self.file_name = file_path[ -1 ]
            self.file_path = tuple( file_path[ 0 : -1 ] )

    def find_or_add_folder( self, root_folder: FolderRef ) -> FolderRef :
        current_ref_folder = root_folder

        for path_part in self.file_path :
            if path_part not in current_ref_folder.subfolders :
                current_ref_folder.subfolders[ path_part ] = FolderRef()

            current_ref_folder = current_ref_folder.subfolders[ path_part ]

        return current_ref_folder

    def archive( self, buffer: BytesIO, instance_index: int, folder_index: int ) :
        nat32( buffer, 1 ) # flags
        string( buffer, self.file_name )
        nat32( buffer, instance_index )
        nat32( buffer, self.use_fid )
        nat32( buffer, folder_index )

class ResourceExternalRef( ExternalRef ) :

    def __init__( self, resource_index: int, use_fid = False ) :
        ExternalRef.__init__( self, use_fid )
        self.resource_index = resource_index

    def archive( self, buffer: BytesIO, instance_index: int, folder_index: int ) :
        nat32( buffer, 5 ) # flags
        nat32( buffer, self.resource_index )
        nat32( buffer, instance_index )
        nat32( buffer, self.use_fid )

class GbxArchive( GbxContainer ) :

    def __init__( self, class_id: int, validators: dict[str, Callable[[Any], bool]] = {}, ancestor_level = 0 ) :
        GbxContainer.__init__( self )

        self.__instances = 0
        self.__validators = validators
        self.__root_folder = FolderRef()
        self.__header_chunks: list[HeaderChunk] = []
        self.__external_refs: list[tuple[ExternalRef, FolderRef, int]] = []

        self.class_id = class_id
        self.ancestor_level = ancestor_level

    def add_instance( self, write = True ) -> int :
        self.__instances += 1

        if write :
            self.nat32( self.__instances )

        return self.__instances

    def header_chunk( self, header_chunk: HeaderChunk ) :
        self.__header_chunks.append( header_chunk )

    def external_ref( self, external_ref: ExternalRef ) :
        self.__external_refs.append( ( external_ref, external_ref.find_or_add_folder( self.__root_folder ), self.add_instance() ) )

    def mw_ref( self, function, *function_args, **function_kwargs ) :
        valid_ref = \
            not function.__name__ in self.__validators \
                or \
            self.__validators[ function.__name__ ]( *function_args, **function_kwargs )

        instance_index = -1
        function_result = None

        if not valid_ref :
            self.nat32( instance_index )
        else :
            instance_index = self.add_instance()
            function_result = function( self, *function_args, **function_kwargs )

        return ( valid_ref, function_result, instance_index )

    def do_save( self, filepath: str ) :
        header = BytesIO()

        text( header, "GBX" )
        nat16( header, 6 )
        text( header, "BUCR" )
        nat32( header, self.class_id )

        header_chunk_count = len( self.__header_chunks )

        if header_chunk_count :
            header_chunk_entries = BytesIO()
            header_chunk_buffers = BytesIO()

            header_chunks_size = 4
            nat32( header_chunk_entries, header_chunk_count )

            for header_chunk in self.__header_chunks:
                header_chunk_data = header_chunk.buffer.getvalue()
                header_chunk_size = len( header_chunk_data )

                header_chunks_size += 8 + header_chunk_size

                if header_chunk.is_heavy :
                    header_chunk_size |= 0x80000000

                nat32( header_chunk_entries, header_chunk.header_chunk_id )
                nat32( header_chunk_entries, header_chunk_size )
                data( header_chunk_buffers, header_chunk_data )

            nat32( header, header_chunks_size )
            data( header, header_chunk_entries )
            data( header, header_chunk_buffers )
        else :
            nat32( header, 0 )

        nat32( header, self.__instances + 1 )
        nat32( header, len( self.__external_refs ) )

        if len( self.__external_refs ) :
            nat32( header, self.ancestor_level )

            self.__root_folder.archive( header, None )

            ref_folders_flat: list[FolderRef] = []
            self.__root_folder.to_list( ref_folders_flat )

            for external_ref, ref_folder, instance_index in self.__external_refs :
                external_ref.archive( header, instance_index, ref_folders_flat.index( ref_folder ) )

        body = self.buffer.getvalue()
        nat32( header, len( body ) )
        body = lzo.compress( body, 9, False )
        nat32( header, len( body ) )
        header = header.getvalue()

        file = open( filepath, 'wb' )
        file.write( header )
        file.write( body )
        file.close()