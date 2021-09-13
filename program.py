class RoomInfo:
    def __init__(self, byte_array):
        self.xs, \
        self.ys, \
        self.xe, \
        self.ye, \
        self.layoutid = byte_array
    def __repr__(self):
        return f'<X coord:{self.xs}:{self.xe} | Y coord:{self.ys}:{self.ye} | LayoutID:{self.layoutid}>'

class TileLayoutInfo:
    def __init__(self, tuple_psx_ptr):
        self.fg_layer, self.bg_layer = tuple_psx_ptr
    def __repr__(self):
        return f'<Foreground Pointer:{self.fg_layer} | Background Pointer:{self.bg_layer}>'

class SotNFile:
    def __init__(self, filename):
        self.data = open(filename, 'rb').read()
        self._generate_data_structures()

    def _generate_data_structures(self):
        self._process_zone_info()
        self._process_layers_info()

    def _process_layers_info(self):
        self.ptrs_list = []
        tile_obj = TileLayoutInfo( \
            (self._read_offset_at_address(0x20), self._read_offset_at_address(0x24)) \
            )
        self.ptrs_list.append(tile_obj)

    def _process_zone_info(self):
        STRUCT_SIZE = 8
        USEFUL_BYTES = 5
        EOF_CHECK_SIZE = 4

        offset = self._read_offset_at_address(0x10)
        byte_stream = self.data[offset:]
        self.room_list = []
        while byte_stream[:EOF_CHECK_SIZE].hex() != '40000000':
            self.room_list.append(RoomInfo(byte_stream[:USEFUL_BYTES]))
            byte_stream = byte_stream[STRUCT_SIZE:]

    def _del_psx_offset(self, global_offset):
        MAGIC_OFFSET_NUMBER = 0x80180000
        return global_offset - MAGIC_OFFSET_NUMBER

    def _read_offset_at_address(self, hex_base_offset):
        BYTES_FOR_32BITS = 4
        # [::-1] because is little endian
        return self._del_psx_offset(int.from_bytes(self.data[hex_base_offset:hex_base_offset + BYTES_FOR_32BITS], byteorder='little'))

    def __repr__(self):
        return f'\n<Zone Info:{self.room_list}\nTile Layer Info:{self.ptrs_list}>\n'


def main():
    # ST0  <- Final Stage: Bloodletting
    from pprint import pprint
    print('Intro:', SotNFile("sotn-iso-map-dump/ST/ST0/ST0.BIN"))
    print('Maria Clock Tower:', SotNFile("sotn-iso-map-dump/BOSS/MAR/MAR.BIN"))
    print('Alucard Nightmare:', SotNFile("sotn-iso-map-dump/ST/DRE/DRE.BIN"))

if __name__ == '__main__':
    main()
