===============================================================================================

                              Castlevania: Symphony of the Night

===============================================================================================
                              Zone files technical documentation
-----------------------------------------------------------------------------------------------

===============================================================================================
                          Reverse Engineered, Researched, and Written
                                        by Nyxojaele
===============================================================================================
                               Special thanks to Gemini and Esco
-----------------------------------------------------------------------------------------------
                                          version 1.0


+++++++++++++++++++++++++++++
      Table of Contents
+++++++++++++++++++++++++++++
What is this?          [INTRO]
Terms and glossary     [TERMS]
Basic file overview    [BASIC]
Decompressing Graphics [DCOMP]
The Map Tiles File     [MAPTF]
The Map Data File      [MAPDF]
Zone Layout            [LYOUT]
Tiles Layout           [TILES]
Entity Graphics        [NTGFX]
Entity Layout          [NTITY]
Tidbits of Info        [TDBIT]



    [INTRO]  What is this?
This document is meant to be a centralized place containing all known information about the
SotN map files' format.



    [TERMS]  Terms and glossary
There are certain terms that will be used throughout this document that you will be expected
to know without the need to explain them.  These terms will for the most part be documented
here:

 * PSX      <- Playstation.
 * SotN     <- Castlevania: Symphony of the Night. This game.
 * RGBA     <- Red, Green, Blue, Alpha: Usually in reference to how a color is stored in bytes.
               In modern-day systems, this is usually 8bits of red, 8bits of green, 8bits of
               blue, then 8bits of alpha transparency. This is often called true color, and is
               4bytes each.  On the PSX, this is 5bits of red, 5bits of green, 5 bits of
               blue, and a single bit of transparency. This is called 16bit color, and is
               2bytes each.
 * CLUT     <- Color LookUp Table: This is a series of 16 RGBA colors referenced by tiles to
               decide what color each individual pixel of that tile is.  Many PSX games use
               256 color CLUTs, but SotN only uses 16 color CLUTs.
 * Tile     <- A single 16x16 pixel graphic that is used to display the game world. A tile is
               composed of 256 values, each of which is 1 nybble (4 bits) big. Each value is
               a number from 0-15, which is the index of the color in the associated CLUT that
               the pixel in question is to use.
 * Entity   <- A single dynamic object in the game world.  This includes monsters, torches,
               items, many secret passages, doors, and even Alucard himself.
 * Room     <- A single room, that can have any tile dimensions that are a multiple of 16. This
               means the minimum size a room can be is 256x256 pixels (16x16 tiles). Many rooms
               also contain a collection of entities to give it flavor.
 * Zone     <- A collection of rooms that represent a single area of the game world. Examples
               of this would be "The Catacombs" or "The Laboratory".
 * VRAM     <- Video RAM: The PSX has video ram stored in such a manner that the only way to
               access it is via X & Y coordinates, instead of just a single stream of bytes.
               This means a couple of things- one being that it's only really logical to store
               pixel values in the VRAM, and the other being that it is relatively easy to
               organize your graphical data in the VRAM.  Because of the fact that the VRAM is
               only 1mb in size, that means you can only store 4096x512 "tile pixels" (256x32
               full tils).  Alternatively, if you wanted to store RGBA values, you could only
               fit 1024x512 individual colors (64x512 CLUTs).  SotN divides the VRAM based on
               the type of data, for organizational purposes: The top left 1/4 is used to store
               2 buffers for drawing the game world to screen. The top right 1/4 is used to
               store all the tiles loaded for the current zone.  The bottom left 1/4 is used to
               store all the entity graphics for the current zone, and the bottom right 1/4 is
               used to store all the "general use" graphics, some of which are tiles, some of
               which are entity graphics (this includes HUD graphics, and save/load room tiles,
               for reasons I will explain later)
 * PSXPtr   <- PSX Pointer: This is a 32bit value that is an absolute address of a memory
               location on the PSX.  The PSX stores it's cached RAM (the by far most frequently
               type of RAM) using a virtual addressing system, which basically means that
               memory addresses start at 0x80000000 and end at 0x80200000 (2mb total).  99.9%
               of PSXPtrs encountered in SotN will be pointing to this range, the other 0.1%
               are generally only needed when you start looking into the raw DMA channel
               requests for interacting with the VRAM.  There are a couple of important
               address (ranges) to be aware of: 0x800A0000 is the location of the main
               executable (DRA.BIN) and 0x80180000 is the location of the current Map Data File
               in RAM.  You will get to know this last value very well.

 *** Take note that all values as they exist in the file are stored as little-endian values!
 *** This means that the values as seen in a hex editor may not look the same as the values
 ***     after they've been read for use!
 *** If you were to need 1 byte of that data, it would look the same
 *** If you were to need 2 or more bytes of data (for a 16 or 32 bit integer value, for
 ***     example), the data will appear out of order.
 *** For example, assume the following data as seen in a hex editor: 0xAC 0xE2 0x18 0x80
 *** 1 byte would appear as 0xAC
 *** 2 bytes would appear as 0xE2AC
 *** 4 bytes would appear as 0x8018E2AC
 *** Always pay attention to how much data needs to be read so you can properly understand
 ***     the values that are being represented!



    [BASIC]  Basic file overview
The SotN map is divided into zones, each of which is easy to differentiate from the rest
in-game by the way the game displays the zone's name when the player first enters it. Each zone
is made up of 4 files:

 * F_XXX.BIN     <- The map tiles file
 * XXX.BIN       <- The map data file
 * SD_ZKXXX.VH   <- The map audio header file
 * SD_ZKXXX.VB   <- The map audio binary file

    |||Zones and Bosses|||
The basic maps can be found at ISO://ST/XXX/ where XXX is the zone abbreviation. Abbreviations
are as follows:

 * ARE  <- Colosseum
 * CAT  <- Catacombs
 * CEN  <- Center Cube Area (Final Boss)
 * CHI  <- Abandoned Mine
 * DAI  <- Royal Chapel
 * DRE  <- Nightmare
 * LIB  <- Long Library
 * MAD  <- Debug Area. Unused ingame.
 * NO0  <- Marble Gallery
 * NO1  <- Outer Wall
 * NO2  <- Olrox's Quarters
 * NO3  <- Castle Entrance
 * NO4  <- Underground Caverns
 * NP3  <- Castle Entrance (After entering Alchemy Laboratory)
 * NZ0  <- Alchemy Laboratory
 * NZ1  <- Clock Tower
 * SEL  <- Game Loading Screen (There are no tiles in this file- only entities!)
 * ST0  <- Final Stage: Bloodletting
 * TE1  <- A long straight hallway. Very long. Unused ingame.
 * TE2  <- A long straight hallway. Very long. Unused ingame.
 * TE3  <- A long straight hallway. Very long. Unused ingame.
 * TE4  <- A long straight hallway. Very long. Unused ingame.
 * TE5  <- A long straight hallway. Very long. Unused ingame.
 * TOP  <- Castle Keep
 * WRP  <- All warp rooms.
 * RARE <- Reverse Colosseum
 * RCAT <- Floating Catacombs
 * RCEN <- Reverse Center Cube Area (Final Boss)
 * RCHI <- Reverse Mine
 * RDAI <- Anti Chapel
 * RLIB <- Forbidden Library
 * RNO0 <- Black Marble Gallery
 * RNO1 <- Reverse Outer Wall
 * RNO2 <- Death Wing's Lair
 * RNO3 <- Reverse Entrance
 * RNO4 <- Reverse Caverns
 * RNZ0 <- Necromancy Laboratory
 * RNZ1 <- Reverse Clock Tower
 * RTOP <- Reverse Castle Keep
 * RWRP <- All reverse warp rooms.

The boss maps can be found at ISO://BOSS/XXX/ where XXX is the boss abbreviation. Abbreviations
are as follows:

 * BO0  <- Olrox
 * BO1  <- Legion
 * BO2  <- Werewolf & Minotaur
 * BO3  <- Scylla
 * BO4  <- Doppleganger10
 * BO5  <- Hippogryph
 * BO6  <- Richter
 * BO7  <- Cerberus
 * MAR  <- Not actually a boss- it's the first encounter with Maria, at the giant clock in the
           Marble Gallery
 * RBO0 <- Fake Trevor/Grant/Sypha
 * RBO1 <- Beelzebub
 * RBO2 <- Death
 * RBO3 <- Medusa
 * RBO4 <- The Creature
 * RBO5 <- Doppleganger40
 * RBO6 <- Shaft/Dracula
 * RBO7 <- Akmodan II
 * RBO8 <- Galamoth


    |||The Map Tiles File|||
This file contains only raw tile graphics as referenced by the Map Data File.  The data is
all stored as raw data that can be used by the PSX immediateley with no conversion necessary.
Interestingly enough, there is also CLUT data stored in this file, interspersed amongst the
tile graphics, but stored in a different format.


    |||The Map Data File|||
This file contains everything except the raw tile graphics and audio, for the specific zone
this file is a part of.  There is a LOT of very -different- data all lumped together in this
file. It is by far the most complicated file of the bunch, and there is still a lot that is
unknown about it.

Some examples of what can be found in this file include (but is not limited to) the following:

 * Zone layout data, including each individual room's layout data
 * Dynamic map information (including 3d effects such as the clock tower in background)
 * Entity graphics
 * Entity animations
 * Entity AI

What this means is that each zone in the game can define it's own version of any monster you
encounter.  You could find a Bloody Zombie in one zone with completely different stats than
a Bloody Zombie in another zone.


    |||The Map Audio Header File|||
This file contains basic information to help with reading the Map Audio Binary File.


    |||The Map Audio Binary File|||
This file contains the raw audio that is referenced from the Map Data File.



    [DCOMP] Decompressing Graphics
Some graphics encountered are compressed to save space. This compression is not super-complex,
and it vaguely resembles RLE compression. Compressed graphics are stored linearly- that means
to decompress them, all you need to do is read in some compressed values, then output the
appropriate decompressed values. Rinse, repeat. After encountering the "end of graphic" value,
the entire array of decompressed values will be the actual graphic as it should be for loading
into VRAM.

The first 8 bytes are called "common values"- each byte being it's own value. These are values
that show up frequently in the compressed graphic, and later on will be referred to by index.
After the common values, all other values are stored as nybbles (2 values per byte, 4 bits
each)- these values should be read in the following manner:

 1) Read 1 value. This is the opcode- it represents what sort of compression exists for the
    coming value(s), or what action to take (such as the end of compression marker)
 2) Depending on the opcode, there may be parameter values following the opcode. Read these
    values as well.
 3) Calculate what the output values should be and add them to the output array.
 4) If the opcode was NOT the end of compression marker, go back to step 1, starting at the
    position immediately following the parameters, if any, in the compressed data.

The opcodes and parameters are as follows:
    Opcode    What to do with it
    0x0       Read 2 more values. Bitshift the first value left by 4, then add it to the 2nd
              value, and finally add 19 to that value. Append that many 0's (zeroes) to the
              decompressed array.
    0x1       Read 1 more value. Append that value to the decompressed array.
    0x2       Read 1 more value. Append that value twice to the decompressed array.
    0x3       Read 1 more value. Append that value to the decompressed array. Read and Append
              another value.
    0x4       Read 1 more value. Append that value to the decompressed array. Read and Append
              another value. Read and Append a 3rd value.
    0x5       Read 1 more value- This is your desired value. Read another value- This is your
              loop value. Append the desired value to the decompressed array, loop times.
    0x6       Read 1 more value. Append that many 0's (zeroes) to the decompressed array.
    0x7-0xE   Subtract 7 from the opcode and use that as an index into the common values array-
              From that value, the first 4bits are your loop value, and the last 4 bits are
              your desired value. Append your desired value to de decompressed array, loop
              times.
    0xF       Finish. This signals that decompression is done, and no more opcodes should be
              read from the compressed data.



    [MAPTF]  The Map Tiles File
The Map Tiles File contains raw graphics for all the tiles to be used by the zone.  Since it's
just raw data, there's no way to know what colors go with which pixels on any given tile, as
the file contains no referencing data at all.

The file is divided up into 8 slots (each of which represents 256 tiles in a 16x16 grid- that
totals a possible 2048 unique tiles per zone). Within each slot, the data is further divided
into 4 groups (each of which represents 64 tiles in an 8x8 grid).  Each of these groups is
stored linearly, meaning there is no further need to subdivide the data- it can just be loaded
directly into a byte array and imported into VRAM as a 128x128 graphic.

The arrangement of these groups in VRAM is very specific--  Starting at (2048, 0), which is the
top edge of VRAM, but centered horizontally, each slot of tiles is positioned to the immediate
right of the last slot.  Within each slot, the first 2 groups are positioned horizontally, then
the next 2 groups are positioned below the first 2, also in a horizontal fashion.  Here's a
visual to help understand the order the data is actually stored in the file as compared to how
it resides in VRAM- each number represents a single group of 64 tiles.


    | = division between groups
    - = division between groups
    # = division between slots

    1  | 2  # 5  | 6  # 9  | 10 # 13 | 14 # 17 | 18 # 21 | 22 # 25 | 26 # 29 | 30 
   ---------#---------#---------#---------#---------#---------#---------#---------
    3  | 4  # 7  | 8  # 11 | 12 # 15 | 16 # 19 | 20 # 23 | 24 # 27 | 28 # 31 | 32 


The file will -always- contain all 8 slots, even if there's no tile data to fill it (they will
just appear as "blank" tiles)-- this is why these files are always 256k big.  One thing to note
is that the bottom row of tiles on both the 3rd and 4th groups of each slot actually don't
contain tiles, but rather contain a grid of 8x16 CLUTs each. This means that after a Map Tiles
File has been loaded to VRAM, there is potentially up to 2048 CLUTs loaded as well, at the cost
of only up to 128 tiles.

*** As a side note, there are many general use graphics files stored in the root or /BIN
directories of the SotN CD, which contain graphics in much the same way.  Graphics such as the
rendered castle as seen behind the text at the beginning of the game, etc.. can be seen in
this way.



    [MAPDF]  The Map Data File
This file is the meat and potatoes of the zones' data, and is an incredibly complicated and
messy place to try and make sense of.

Take note that this file's format is far from completely reverse engineered as of yet, so
there's a lot of unknown values at this point.  But despite that, most of the interesting data
can currently be read.

The first part of the file is always the header.  This header is always 64bytes long, although
all 64 bytes may NOT actually be header data-- a complete header is composed of 16x PSXPtrs,
each of which represents a subsection of the file. Some zones don't use all 16 subsections
tho, so this header section can actually be cut short by the lack of need for the last few
subsections (and thus, their PSXPtrs in the header). The game doesn't care tho, so it just
loads the first 64bytes of data, whether they're all PSXPtrs or not, into a special area of
RAM reserved to hold the current zone's header data, and if a certain subsection isn't needed
by the current zone, then that particular PSXPtr of the header is just never used (which would
be a bad thing anyways, since it's probably actually a bit of data from the first subsection!)

These subsections, in their current state of known-ness, are as follows:

 * Code1                         <- [Raw code] Something to do with entities.. attacking?
 * Code2                         <- [Raw code] Looks like it mostly deals with respawning
                                    entities
 * Frame_SpawnNearbyEntities     <- [Raw code] Spawns entities based on the screen's current
                                    position and movement. Entities are spawned when they are
                                    within 64 pixels of the boundaries of the screen, assuming
                                    they are not marked as already dead. This code is called
                                    every frame.
 * EnterRoom_SpawnNearbyEntities <- Same as Frame_SpawnNearbyEntities, except this code is only
                                    ever called once, when the player enters a room. It also
                                    sets some RAM values that are used by a lot of other code
                                    to quickly access the correct data for the current room.
 * ZoneLayout                    <- [Data] Address of the zone layout data. This is mostly
                                    data used for the overall zone, as well as how the rooms
                                    in the zone are connected together.
 * SpriteFrameBanks              <- [Data] Address of the raw entity graphics- sometimes
                                    these graphics are broken apart into pieces that are put
                                    together during playtime into a more understandable
                                    graphic.
 * Data1                         <- [Data] Address of other, relatively small, data.
 * Data2                         <- [Data] Address of other data.
 * LayoutDefs                    <- [Data] Address of room layout definitions. This data is
                                    just used to show pairings of layers-- one as the
                                    foreground and one as the background.
 * EntityGraphicDefs             <- [Data] Address of entity graphics definitions. This data
                                    basically takes the entity graphics and ties them together,
                                    as well as placing them all properly in relation to one-
                                    another in order to make it all look like a single graphic.
 * Code3                         <- [Raw code] Checks some state info, initiates entity AI..?
 * SpriteData1                   <- [Data] Address of other data pertaining to sprites.
 * SpriteData2                   <- [Data] Address of other data pertaining to sprites.
 * Data3                         <- [Data] Address of other data.
 * Data4                         <- [Data] Address of other data.
 * Data5                         <- [Data] Address of other data.


There is a lot of data to go thru, so it's going to be divided up into logical portions as
they would make sense for the game to be used- starting with room layouts, and progressing
into populating those rooms with their properties and entities.



    [LYOUT]  Zone Layout
The PSXPntr to this section can be found at offset 0x10 in the Map Data File header. Remember
to subtract 0x80180000 from the PSXPntr value to get the actual offset into the file itself.
At that offset, an array of simple structures representing rooms can be found- these structures
look like this:


 * MapXStart   <- The X position of the left-most block of the room.
 * MapYStart   <- The Y position of the top-most block of the room.
 * MapXEnd     <- The X position of the right-most block of the room.
 * MapYEnd     <- The Y position of the bottom-most block of the room.
 * LayoutID    <- The index of the layout structure that holds info on how the tiles make up
                  the room.
 * TileGfxID   <- Not much is known, but when the room represents a place to load a new zone,
                  this value will be 0xFF.
 * EntGfxID    <- The index of the entity graphics structure that holds info on how to load
                  raw entity graphics into VRAM for use by the room.
 * EntLyoutID  <- The index of the entity layout structure that holds info on how to position
                  and initialize entities in the room.

 *** Each of these values is stored as a single byte
 *** These map positions are what is used by the game to determine how the rooms are all
         connected to each other.
 *** This structure will repeat itself until a MapXStart value equal to 0x40 is found, which
 ***     marks the end of the rooms list. This value will be followed by 0x000000 as padding.



    [TILES]  Tiles Layout
The PSXPntr to this section can be found at offset 0x20 in the Map Data File header. At this
offset , an array of PSXPntr pairs can be seen, each of which represents a foreground and a
background layer for a single layout. Typically this will only be used for a single room, but
there are occassions when more than 1 room may use the same layout:


 * ForegroundLayer   <- A PSXPntr to the layer structure containing info about the foreground
 * BackgroundLayer   <- A PSXPntr to the layer structure containing info about the background

 *** There are many layouts that specify the same PSXPntr for the BackgroundLayer- this is
         often the case when rooms don't have a background layer to speak of, in which case
         this PSXPntr will point to a structure representing a "blank" layer.


    |||Layers|||
Each of these layer PSXPntrs will point to a Layer structure that looks like the following:


 * TileLayout        <- A PSXPntr to the actual tile layout data. This data is an array of
                        16bit values, each of which is an index into a series of other tables
                        that each contain a specific piece of info about that specific tile.
 * TileDefs          <- A PSXPntr to the tile information tables to be used for the layer. Most
                        layers use the same PSXPntr here, as typically, one is enough.
 * RoomDims          <- This is a series of 4 values, each of which is 6 bits long, resulting
                        in only 3 bytes of data being used. This specifies, using the same
                        units as the MapStart/MapEnd values in the Zone Layout, the size of
                        this layer. This is important, as some layers can visually look larger
                        than the space they take up on the map- a prime example of this would
                        be the tall vertical towers- each of these towers is only 1 map square
                        wide, but the background layers, with all the trees and whatnot, are
                        more like 3 map squares wide.
 * RoomFlags         <- A single byte representing a series of flags that somehow affect which
                        TileDefs are being used. Not much is known about this value at this
                        time.
 * LayerOrNewLBAData <- This byte value represents at what point this layer should be drawn as
                        compared to other layers, sprites, etc... A higher value means it
                        should be drawn later (meaning it will appear "closer.")
 * Unknown4          <- The only thing known about this byte value is that when it's set to
                        0x01, this layer becomes a "topmost" layer, drawing in front of
                        everything else on the screen.
 * DrawingFlags      <- Not much is known about this 16bit value. The following flags have been
                        found so far:
                        00000000 00000001 = Draw this layer
                        00000000 00000010 = ? (Usually in conjuction with 00000000 00000001)
                        00000001 00000000 = Changes graphical tileset (no effect on collisions)
                        00000010 00000000 = Use Generic CLUTs for this layer- this value is
                                            especially important as it is used by save/load
                                            rooms, since they don't use tiles stored in the
                                            zone files, but rather, they use CLUTs and tiles
                                            stored in DRA.BIN and F_GAME.BIN.


    |||TileDefs|||
Remember that when looking for data in the TileDef arrays, a single value should be read from
the TileLayout array in the layer structure, and used as an index into ALL of these arrays!
The TileDef PSXPntr in the layer structure points to a structure that looks like the following:


 * Tileset         <- A PSXPntr to an array of 1byte values, each of which represents a set of
                      coordinates to a set of tiles that this tile belongs to. The first 4bits
                      of this value represents the X position (after multiplying it by 256) of
                      the tileset to use. The last 4bits of this value represents the Y
                      position (after multiplying it by 256) of  the tileset to use.
 * TilePos         <- A PSXPntr to an array of 1byte values, each of which represents a set of
                      coordinates to a single tile within it's specified tileset. The first
                      4bits of this value represents the X position (after multiplying it by
                      16) of the tile to use. The last 4bits of this value represents the Y
                      position (after multiplying it by 16) of the tile to use.
 * CLUTCoordsIndex <- A PSXPntr to an array of 1byte values, each of which represents an index
                      into an array of hard-coded coordinates to CLUTs in VRAM. The following
                      is a listing of this array of coordinates:
                          (2048, 240), (2112, 240), (2176, 240), (2240, 240) ... (3072, 240),
                          (2048, 241), (2112, 241), (2176, 241), (2240, 241) ... (3072, 241),
                          (2048, 242), (2112, 242), (2176, 242), (2240, 242) ... (3072, 242),
                          ...
                          (2048, 255), (2112, 255), (2176, 255), (2240, 255) ... (3072, 255)
                      You'll notice that these all correspond to the location in VRAM where the
                      Map Tiles File has stored CLUTs instead of tile graphics.
 * CollisionInfo   <- A PSXPntr to an array of 1bit values, each of which represents a
                      "collision type"- not much is currently known about how these are
                      generated, but all 256 possibilities have been charted out.

                      To read this chart, consider a single tile to have a height of 4- the
                      left and right edges of the top and bottom of this tile can be at any
                      (logical) of these 4 heights, 0 being the topmost, and 4 being the
                      bottommost. The numbers are listed starting with the topleft corner,
                      followed by the topright corner, then the bottomleft, and lastly the
                      bottomright. So an entry "2, 0, 4, 4" means the top left corner is half
                      way down the full height of the tile, the top right corner is as high
                      as possible, and the bottom corners are as low as possible, resulting in
                      a tile with a 22.5 degree slope up and to the right, starting at half the
                      height of the tile. Any entries followed by "H" have no horizontal
                      collision (so an entity can walk thru the tile horizontally, but might
                      not be able to jump/fall thru it vertically). Any entry followed by a *#
                      where # is a numeric value, has special properties that are described
                      after the chart. Lastly, any entry with a X is never used in the existing
                      maps.

                      0   = NOTHING          86  = NOTHING X        172 = NOTHING X
                      1   = 0, 0, 4, 4 H     87  = 0, 0, 4, 4 X     173 = NOTHING X
                      2   = NOTHING X        88  = NOTHING X        174 = NOTHING X
                      3   = 0, 0, 4, 4       89  = 0, 0, 4, 4 HX    175 = NOTHING X
                      4   = NOTHING X        90  = NOTHING X        176 = NOTHING X
                      5   = 0, 0, 4, 4 HX    91  = 0, 0, 4, 4 X     177 = NOTHING X
                      6   = NOTHING X        92  = NOTHING X        178 = NOTHING X
                      7   = 0, 0, 4, 4 X     93  = 0, 0, 4, 4 HX    179 = NOTHING X
                      8   = NOTHING X        94  = NOTHING X        180 = NOTHING X
                      9   = 0, 0, 4, 4 HX    95  = 0, 0, 4, 4 X     181 = NOTHING X
                      10  = NOTHING X        96  = NOTHING X        182 = NOTHING X
                      11  = 0, 0, 4, 4 X     97  = 0, 0, 4, 4 HX    183 = NOTHING X
                      12  = NOTHING X        98  = NOTHING X        184 = NOTHING X
                      13  = 0, 0, 4, 4 HX    99  = 0, 0, 4, 4 X     185 = NOTHING X
                      14  = NOTHING X        100 = NOTHING X        186 = NOTHING X
                      15  = 0, 0, 4, 4 X     101 = 0, 0, 4, 4 HX    187 = NOTHING X
                      16  = NOTHING X        102 = NOTHING X        188 = NOTHING X
                      17  = 0, 0, 4, 4 HX    103 = 0, 0, 4, 4 X     189 = NOTHING X
                      18  = NOTHING X        104 = NOTHING X        190 = NOTHING X
                      19  = 0, 0, 4, 4 X     105 = 0, 0, 4, 4 HX    191 = NOTHING X
                      20  = NOTHING X        106 = NOTHING X        192 = NOTHING X
                      21  = 0, 0, 4, 4 HX    107 = 0, 0, 4, 4 X     193 = NOTHING X
                      22  = NOTHING X        108 = NOTHING X        194 = NOTHING X
                      23  = 0, 0, 4, 4 X     109 = 0, 0, 4, 4 HX    195 = NOTHING X
                      24  = NOTHING X        110 = NOTHING X        196 = NOTHING X
                      25  = 0, 0, 4, 4 HX    111 = 0, 0, 4, 4 X     197 = NOTHING X
                      26  = NOTHING X        112 = NOTHING X        198 = NOTHING X
                      27  = 0, 0, 4, 4 X     113 = 0, 0, 4, 4 HX    199 = NOTHING X
                      28  = NOTHING X        114 = NOTHING X        200 = NOTHING X
                      29  = 0, 0, 4, 4 HX    115 = 0, 0, 4, 4 X     201 = NOTHING X
                      30  = NOTHING X        116 = NOTHING X        202 = NOTHING X
                      31  = 0, 0, 4, 4 X     117 = 0, 0, 4, 4 HX    203 = NOTHING X
                      32  = NOTHING X        118 = NOTHING X        204 = NOTHING X
                      33  = 0, 0, 4, 4 HX    119 = 0, 0, 4, 4 X     205 = NOTHING X
                      34  = NOTHING X        120 = NOTHING X        206 = NOTHING X
                      35  = 0, 0, 4, 4 X     121 = 0, 0, 4, 4 HX    207 = NOTHING X
                      36  = NOTHING X        122 = NOTHING X        208 = NOTHING X
                      37  = 0, 0, 4, 4 HX    123 = 0, 0, 4, 4 X     209 = NOTHING X
                      38  = NOTHING X        124 = NOTHING X        210 = NOTHING X
                      39  = 0, 0, 4, 4 X     125 = 0, 0, 4, 4 HX    211 = NOTHING X
                      40  = NOTHING X        126 = NOTHING X        212 = NOTHING X
                      41  = 0, 0, 4, 4 HX    127 = 0, 0, 4, 4       213 = NOTHING X
                      42  = NOTHING X        128 = 4, 0, 4, 4       214 = NOTHING X
                      43  = 0, 0, 4, 4 X     129 = 0, 0, 4, 4 *1    215 = NOTHING X
                      44  = NOTHING X        130 = 0, 0, 4, 4 *2    216 = NOTHING X
                      45  = 0, 0, 4, 4 HX    131 = 0, 4, 4, 4       217 = NOTHING X
                      46  = NOTHING X        132 = 0, 0, 0, 4       218 = NOTHING X
                      47  = 0, 0, 4, 4 X     133 = 0, 0, 4, 4 *3    219 = NOTHING X
                      48  = NOTHING X        134 = 0, 0, 4, 4 *4    220 = NOTHING X
                      49  = 0, 0, 4, 4 HX    135 = 0, 0, 4, 0       221 = NOTHING X
                      50  = NOTHING X        136 = 4, 2, 4, 4       222 = NOTHING X
                      51  = 0, 0, 4, 4 X     137 = 2, 0, 4, 4       223 = NOTHING X
                      52  = NOTHING X        138 = 0, 0, 4, 4 *5    224 = NOTHING X
                      53  = 0, 0, 4, 4 HX    139 = 0, 0, 4, 4 *6    225 = NOTHING X
                      54  = NOTHING X        140 = 0, 2, 4, 4       226 = NOTHING X
                      55  = 0, 0, 4, 4 X     141 = 2, 4, 4, 4       227 = NOTHING X
                      56  = NOTHING X        142 = 0, 0, 0, 2       228 = NOTHING X
                      57  = 0, 0, 4, 4 HX    143 = 0, 0, 2, 4       229 = 2, 2, 2, 2 X*13
                      58  = NOTHING X        144 = 0, 0, 4, 4 *7    230 = 4, 4, 4, 4 X*14
                      59  = 0, 0, 4, 4 X     145 = 0, 0, 4, 4 *8    231 = 0, 0, 0, 0 *15
                      60  = NOTHING X        146 = 0, 0, 4, 3       232 = 2, 2, 2, 2 *16
                      61  = 0, 0, 4, 4 HX    147 = 0, 0, 2, 0       233 = 0, 0, 0, 0 X*17
                      62  = NOTHING X        148 = 4, 3, 4, 4       234 = NOTHING *18
                      63  = 0, 0, 4, 4 X     149 = 3, 2, 4, 4       235 = NOTHING X
                      64  = NOTHING X        150 = 2, 1, 4, 4       236 = NOTHING X
                      65  = 0, 0, 4, 4 HX    151 = 1, 0, 4, 4       237 = NOTHING *19
                      66  = NOTHING X        152 = 0, 0, 4, 4 *9    238 = 0, 0, 4, 4 *20 X
                      67  = 0, 0, 4, 4 X     153 = 0, 0, 4, 4 *10   239 = 0, 0, 4, 4 *21 X
                      68  = NOTHING X        154 = 0, 1, 4, 4       240 = 0, 0, 4, 4 *22 X
                      69  = 0, 0, 4, 4 HX    155 = 1, 2, 4, 4       241 = 0, 0, 4, 4 *23 X
                      70  = NOTHING X        156 = 2, 3, 4, 4       242 = 0, 0, 4, 4 *24
                      71  = 0, 0, 4, 4 X     157 = 3, 4, 4, 4       243 = 0, 0, 4, 4 *25 X
                      72  = NOTHING X        158 = 0, 0, 0, 1       244 = NOTHING *26
                      73  = 0, 0, 4, 4 HX    159 = 0, 0, 1, 2       245 = NOTHING *27 X
                      74  = NOTHING X        160 = 0, 0, 2, 3       246 = NOTHING *28 X
                      75  = 0, 0, 4, 4 X     161 = 0, 0, 3, 4       247 = NOTHING *29 X
                      76  = NOTHING X        162 = 0, 0, 4, 4 *11   248 = 0, 0, 4, 4 *30
                      77  = 0, 0, 4, 4 HX    163 = 0, 0, 4, 4 *12   249 = NOTHING *31
                      78  = NOTHING X        164 = 0, 0, 4, 3       250 = 4, 4, 4, 4 X*32
                      79  = 0, 0, 4, 4 X     165 = 0, 0, 3, 2       251 = 0, 0, 4, 4 X*33
                      80  = NOTHING X        166 = 0, 0, 2, 1       252 = 0, 0, 2, 2 H
                      81  = 0, 0, 4, 4 HX    167 = 0, 0, 1, 0       253 = 2, 2, 4, 4 H
                      82  = NOTHING X        168 = NOTHING X        254 = 0, 0, 2, 2
                      83  = 0, 0, 4, 4 X     169 = NOTHING X        255 = 2, 2, 4, 4
                      84  = NOTHING X        170 = NOTHING X
                      85  = 0, 0, 4, 4 HX    171 = NOTHING X

                  *1 = Unknown use. When possible, appears directly below 128
                  *2 = Unknown use. When possible, appears directly below 131
                  *3 = Unknown use. When possible, appears directly above 132
                  *4 = Unknown use. When possible, appears directly above 135
                  *5 = Unknown use. When possible, appears directly below 136
                  *6 = Unknown use. When possible, appears directly below 141
                  *7 = Unknown use. When possible, appears directly above 142
                  *8 = Unknown use. When possible, appears directly above 147
                  *9 = Unknown use. When possible, appears directly below 148
                  *10 = Unknown use. When possible, appears directly below 157
                  *11 = Unknown use. When possible, appears directly above 158
                  *12 = Unknown use. When possible, appears directly above 167
                  *13 = Unknown use. Never used
                  *14 = Unknown use. Never used
                  *15 = A platform that can be jumped up thru, or dropped down from
                  *16 = A platform that can be jumped up thru, or dropped down from
                  *17 = Unknown use. Never used
                  *18 = Marks water, significantly hinders movement (moreso upon entry)
                  *19 = Marks water, significantly hinders movement
                  *20 = Unknown use. Never used
                  *21 = Unknown use. Never used
                  *22 = Unknown use. Never used
                  *23 = Unknown use. Never used
                  *24 = Breakable tile. When attacked, this tile becomes traversable.
                  *25 = Unknown use. Never used
                  *26 = Causes player to get hurt. (ie spikes)
                  *27 = Unknown use. Never used
                  *28 = Unknown use. Never used
                  *29 = Unknown use. Never used
                  *30 = Passable only in mist form. (ie grates)
                  *31 = Marks water, significantly hinders movement (moreso upon entry)
                  *32 = Unknown use. Never used
                  *33 = Unknown use. Never used



    [NTGFX] Entity Graphics
Whenever a room is entered by the player, all the associated entity graphics are loaded into
VRAM to be used by the entities in the room. An array of PSXPntrs representing all the
available graphics packages can be found by following the EntityGraphicDefs PSXPntr in the
Map Data File header. The EntGfxID value in the Zone Layout structure is an index into this
array. Following this graphics package PSXPntr will lead to the following structure:


 * StartOfPackageMarker <- Valid value is 0x00000000. This means the following values are a
                           valid entry. If this value is 0x00000004, there are no following
                           values (ie the previous package was the final one in the array)
    *** The next 5 values are repeated until EndOfPackageMarker is encountered
 * VRAMYPos             <- 16bit Y position in VRAM to place the graphics
 * VRAMXPos             <- 16bit X position in VRAM to place the graphics
 * Height               <- 16bit height of graphics in VRAM
 * Width                <- 16bit width of graphics in VRAM
 * GfxData              <- PSXPntr to raw graphics data. This data is compressed. See
                           "Decompressing Graphics" for more info on decompressing it.
 * EndOfPackageMarker   <- Always 0xFFFFFFFF. It's just there to mark that there's no more
                           graphics in this package.



    [NTITY] Entity Layouts
The layout structures exist in the Map Data File, but unfortunately do not have any direct
PSXPntrs to them-- instead, there are direct links to the structures from within the
Frame_SpawnNearbyEntities and EnterRoom_SpawnNearbyEntities code. These codebases appear to be
largely the same between all the different zones' Map Data Files, where the only difference is
the actual addresses that are hard-coded into the code itself. This document will not discuss
this code, and will instead provide an easy means thru which to find the actual addresses of
the entity layout structures.

The first thing to note about the entity layouts is that there is actually 2 entity layouts
per room: one is sorted based on the X position of the entities, and the other is sorted based
on the Y position of the entities. This is for ease of finding entities for spawning during
the earlier mentioned spawning functions. That in mind, you can safely ignore one or the other
of these structures, as, when you get down to it, they're just duplicates of each other with
different ordering.

The X-Sorted entity layout array can be found by reading a 16bit value from the location
(EnterRoom_SpawnNearbyEntities + 28). Take note that this value is NOT a PSXPntr! It is an
actual offset from the beginning of the file, to the beginning of the X-Sorted entity layout
array.

The Y-Sorted entity layout array can be found by reading a 16bit value from the location
(EnterRoom_SpawnNearbyEntities + 40). Take note that this value is NOT a PSXPntr! It is an
actual offset from the beginning of the file, to the beginning of the Y-Sorted entity layout
array.

These arrays are composed of a single PSXPntr per entry. Each of these PSXPntrs leads to the
following structure representing the entire room's entity layout:


 *** The following 5 values will repeat until the first one is equal to 0xFFFFFFFF, marking
 *** the end of the entity list for the current room.
 * XPos            <- This 16bit value represents where, in pixels (not tiles!) the entity is
                      initially placed on the X-axis in the room.
 * YPos            <- This 16bit value represents where, in pixels (not tiles!) the entity is
                      initially placed on the Y-axis in the room.
 * EntityID        <- This 16bit value is actually 3 values: The first 3 bits store an unknown
                      value, the next 3 bits store another unknown value, and the last 10 bits
                      store the entity type value. The entity type value is what determines
                      which entity will be placed at this position in the room. The relation
                      between the actual ID stored here and the actual entity that appears
                      in-game is only guaranteed for a single Map Data File! A value of 0x1 may
                      display a candle in one Map Data file, but display a bloody zombie in
                      another Map Data File! This is because this value is actually an index
                      into an array of entity AI PSXPntrs that immediately follow the Y-Sorted
                      entity layout array. Finding this array is described below.
 * Slot            <- This 16bit value is actually 3 values: The first 3 bits store the index
                      of the DeathSlot variable to use, the middle bits are unknown, and the
                      last 4 bits are the actual DeathSlot value to use. DeathSlots are just a
                      way for the game to keep track of which entities in a room have died
                      already or not. There are a total of 6 DeathSlots, each of which is a
                      collection of flags, and each entity in the room must have a unique
                      DeathSlot index/value combination. Note that since DeathSlots are 16bit
                      flag collections, the DeathSlot value must be a power of 2 and no greater
                      than 65,536. These limitations on DeathSlots means that there cannot be
                      more than 96 killable entities in a single room.
 * InitialState    <- This 16bit value is actually 2 values to which no documentation currently
                      exists (sorry!). One of these values is the major state of the entity,
                      and the other value is the sub state of the entity.  The meaning of a
                      major or sub state is entirely up to the entity's AI code.  Typically
                      however, the major state will have at least an "Initialization" state
                      equal to 0 or 1, where the AI sets up the entity for use, then sets the
                      major state to an "Idle" state where the entity actually interacts with
                      it's surroundings. Some major states require sub states depending on how
                      the AI code functions for that particular entity, such as an "attack"
                      state composed of 3 separate sub states: "begin attack", "during attack",
                      and "end attack" animations.


    |||Entity AI|||
All entities' AI can be found via an array of PSXPntrs.  Unfortunately the beginning of this
array is not an easy thing to find, as all the code that references any of it's entries has a
pointer to the first entry of the Y-Sorted entity layout array and an index of the AI entry
needed, as if the entity AI array was a PART of the Y-Sorted entity layout array. This is
particularly troublesome as there's no particularly simple way to find the place where the
Y-Sorted entity layout entries end and the Entity AI entries begin.

The best way found so far is to peruse the Y-Sorted entity layout array, taking note of the
first PSXPntr value. Continue thru the array until you encounter that same value again- there
will likely be multiple entries at this point that are all the same as the first entry. The
first entry you encounter from this point on, that is DIFFERENT than that first entry, is the
beginning of the Entity AI entries in the array. Each of these Entity AI entries is a PSXPntr
that points to raw MIPS code. This code is run once per frame by the game to determine
everything dynamic about the entity- this includes, but is not limited to graphics, animations,
movement, spawning subentities (such as projectiles), attacks, blocking/dodging, and death.

Within the Entity AI code can be found references to entity sprite definitions. These are hard-
coded pointers to various places in the Map Data File to find metadata in regards to taking the
graphics in the VRAM and piecing it together (if required) on-screen in the proper format so it
appears as a single entity.

An array of PSXPntrs for all existing entity spritebanks (each of which represents a specific
entity, such as a candle, or a medusa head) can be found by following the SpriteFrameBanks
PSXPntr in the Map Data File header. These SpriteBanks are tied directly to the Entity AI in
that only the Entity AI code knows which SpriteBank to use for itself, and that is all. The
index of a particular entity's spritebank is stored somewhere in the Entity AI code, and the
position of that value in the code is not consistent between Entity AI codebases. Additionally,
following one of these SpriteBank PSXPntrs will lead to another array of PSXPntrs, the first
value of which is always NULL (0), and each entry of which represents a single frame of
animation for the entity in question. Again, the index of each of these frames of animation is
hard-coded in the Entity AI code. Following one of these SpriteFrame PSXPntrs will lead to the
following structure:


    |||Header|||
 * PartCountMapping  <- This 16bit value's 1st bit is a flag indicating whether mapping data
                        should be used to piece together the sprite. The last 15 bits are a
                        count of how many parts will follow if it's mapped, or the part index
                        if it's not.
 
    |||Parts - this body only follows if this sprite frame is mapped|||
 * Flags             <- This 16bit value is a collection of flags as follows:
                        0x00000001 = Flip vertically
                        0x00000010 = Flip horizontally
                        All other values appear to have no effect. Also note that sometimes
                        setting the "Flip vertically" flag generates garbage graphically.
                        Currently it is unknown why this occurs.
 * DestX             <- 16bit X position in VRAM where the current part is to be drawn.
 * DestY             <- 16bit Y position in VRAM where the current part is to be drawn.
 * DestW             <- 16bit width in VRAM that the current part is to be drawn as.
 * DestH             <- 16bit height in VRAM that the current part is to be drawn as.
 * CLUT              <- 16bit value representing which CLUT to use. Currently undocumented.
 * TexturePage       <- 16bit value representing which TexturePage to read graphics from.
                        Currently undocumented.
 * TexCoordU0        <- 16bit value representing the X position in the TexturePage that will
                        be the left edge of the rectangle to use as the source graphic.
                        Currently undocumented.
 * TexCoordV0        <- 16bit value representing the Y position in the TexturePage that will
                        be the top edge of the rectangle to use as the source graphic.
                        Currently undocumented.
 * TexCoordU1        <- 16bit value representing the X position in the TexturePage that will
                        be the right edge of the rectangle to use as the source graphic.
                        Currently undocumented.
 * TexCoordV1        <- 16bit value representing the Y position in the TexturePage that will
                        be the bottom edge of the rectangle to use as the source graphic.
                        Currently undocumented.

    |||Position - this body only follows if this sprite frame is unmapped|||
 * DestXOffset       <- 16bit value representing the X position to draw at. Currently
                        undocumented.
 * DestYOffset       <- 16bit value representing the Y position to draw at. Currently
                        undocumented.



    [TDBITS] Tidbits of Info
It is currently known that the SpriteData1 and SpriteData2 PSXPntrs in the Map Data File header
point to arrays of structures that contain additional sprite drawing data for use under certain
circumstances. Since this data is not always required, some Map Data Files do not make use of
these PSXPntrs, and they instead point to garbage. The actual structures have yet to be
documented.e
