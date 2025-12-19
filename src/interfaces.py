from pymtl3 import *

class StreamMsg( BitStruct ):
    # Definim structura datelor: doar pixelul (8 biti) momentan
    # Putem adauga flags (Start of Frame, End of Line) mai tarziu
    data: Bits8

class StreamInterface( Interface ):
    def construct( s, Type ):
        s.msg = InPort( Type )
        s.val = InPort( Bits1 )
        s.rdy = OutPort( Bits1 )

    def connect_stream( s, other ):
        s.msg //= other.msg
        s.val //= other.val
        s.rdy //= other.rdy

# Helper pentru porturile de intrare/iesire
class StreamInPort( CallerPort ):
    def construct( s, Type ):
        s.msg = OutPort( Type ) # Caller trimite datele
        s.val = OutPort( Bits1 )
        s.rdy = InPort( Bits1 )

class StreamOutPort( CalleePort ):
    def construct( s, Type ):
        s.msg = InPort( Type )
        s.val = InPort( Bits1 )
        s.rdy = OutPort( Bits1 )