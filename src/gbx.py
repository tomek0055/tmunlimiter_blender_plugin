from io import BytesIO
import struct
import lzo

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

    def __init__( self, class_id : int, validators : dict = {} ) :
        self.mw_ids = []
        self.mw_id_used = False

        self.body = BytesIO()

        self.class_id = class_id
        self.instances = 0

        self.validators = {
            **validators,
            "plug_visual_3d" : lambda object : object.type == "MESH"
        }

    def nat8( self, value : int ) :
        nat8( self.body, value )

    def nat16( self, value : int ) :
        nat16( self.body, value )

    def nat32( self, value : int ) :
        nat32( self.body, value )

    def real( self, value : int ) :
        real( self.body, value )

    def string( self, value : str ) :
        string( self.body, value )

    def mw_id( self, mw_id : str = "" ) :
        if not self.mw_id_used :
            self.mw_id_used = True
            self.nat32( 0x00000003 )

        if len( mw_id ) == 0 :
            self.nat32( 0xFFFFFFFF )
        elif mw_id in self.mw_ids :
            self.nat32( 0x40000001 + self.mw_ids.index( id ) )
        else :
            self.mw_ids.append( mw_id )
            self.nat32( 0x40000000 )
            self.string( mw_id )

    def mw_ref( self, function, *function_args, **function_kwargs ) :
        valid_ref = not function.__name__ in self.validators or self.validators[ function.__name__ ]( *function_args, **function_kwargs )

        if not valid_ref :
            self.nat32( 0xFFFFFFFF )
            return

        self.instances += 1
        self.nat32( self.instances )

        function( self, *function_args, **function_kwargs )

    def do_save( self, filepath : str ) :
        header = BytesIO()

        text( header, "GBX" )
        nat16( header, 6 )
        text( header, "BUCR" )
        nat32( header, self.class_id )
        nat32( header, 0x00000000 )
        nat32( header, self.instances + 1 )
        nat32( header, 0x00000000 )

        body = self.body.getvalue()
        nat32( header, len( body ) )
        body = lzo.compress( body, 9, False )
        nat32( header, len( body ) )
        header = header.getvalue()

        file = open( filepath, 'wb' )
        file.write( header )
        file.write( body )
        file.close()