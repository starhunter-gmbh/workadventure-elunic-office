"""Gameplay data for the painted new office map (newoffice-art.png, 1952x800 px = 61x25 tiles).

Collisions are measured by hand on the tile grid of the art (tile rectangles, inclusive): WALLS and BLOCK are blocked,
DOORS and every seat tile are walkable again. Seats are pixel centres (x, y, facing towards the table) detected from
the chair/cushion blobs in the art. Rooms and areas are pixel rectangles (x0, y0, x1, y1), end exclusive.
"""
ART = 'newoffice-art.png'

def T(x0, y0, x1=None, y1=None):
    """Tile rectangle, inclusive; T(x, y) is one tile."""
    return (x0, y0, x0 if x1 is None else x1, y0 if y1 is None else y1)

WALLS = [
    T(0, 0, 60, 0), T(0, 24, 60, 24), T(0, 0, 0, 24), T(60, 0, 60, 24),          # outer shell
    T(18, 1, 18, 9),                                                            # lounge | WC block
    T(0, 9, 5, 9),                                                              # lounge | focus booths
    T(4, 10, 4, 23), T(1, 13, 3, 13), T(1, 16, 3, 16), T(1, 20, 3, 20),         # booth fronts and partitions
    T(21, 4, 24, 4), T(21, 5, 21, 8), T(21, 8, 25, 8), T(25, 1, 25, 8),         # restroom, women
    T(25, 8, 37, 8), T(37, 1, 37, 8),                                           # stair core
    T(38, 8, 40, 8), T(40, 1, 40, 8),                                           # men
    T(41, 6, 41, 6), T(43, 1, 43, 9),                                           # server | side corridor | kitchen
    T(44, 9, 59, 9),                                                            # kitchen | corridor
    T(54, 10, 54, 13), T(35, 13, 54, 13),                                       # corridor end, meeting rooms
    T(35, 14, 35, 23), T(39, 14, 39, 23), T(45, 14, 45, 23),                    # small meeting | meeting 4 | large
    T(26, 17, 34, 17), T(26, 18, 26, 23), T(30, 18, 30, 23),                    # phone rooms (glass front, walls)
]
DOORS = [
    T(4, 11), T(4, 15), T(4, 18), T(4, 22),                                     # focus booths
    T(21, 6), T(30, 8), T(31, 8), T(32, 8),                 # restroom, women, entrance
    T(40, 7), T(42, 6), T(53, 9), T(54, 11), T(37, 13), T(43, 13),              # men, server, kitchen, meetings
    T(29, 17), T(31, 17),                                                       # phone rooms
]
BLOCK = [
    # lounge: plants, sofa backs, coffee table, TV, round table, table tennis, foosball
    T(1, 2), T(1, 4), T(1, 8), T(17, 2), T(17, 9), T(3, 1, 6, 1), T(3, 5, 5, 6), T(10, 1, 10, 4), T(14, 4, 14, 5),
    T(7, 8, 9, 11), T(13, 9, 14, 10),
    # focus booths: desks; open space: plant, desks (docked at the window wall)
    T(1, 11, 1, 12), T(1, 14, 1, 15), T(1, 18, 1, 19), T(1, 22, 1, 23),
    T(6, 12), T(7, 15, 8, 23), T(12, 15, 13, 23), T(17, 15, 18, 23), T(22, 15, 23, 23),
    # WCs: restroom sink, shower, half wall, toilet; women sink, toilet; men toilet
    T(19, 1), T(22, 3), T(23, 3), T(24, 3), T(22, 7), T(24, 7), T(38, 1, 39, 1), T(38, 2), T(38, 5),
    # stair core: elevators and stairs, plants; server rack
    T(27, 1, 36, 5), T(26, 7), T(36, 7), T(41, 1, 42, 3),
    # corridor: sideboards, coat rack, gong
    T(21, 9, 23, 9), T(26, 9, 28, 10), T(25, 9), T(38, 9, 40, 9),
    # reception counter (arch, staff inside), plants; phone desks, plant
    T(27, 13, 33, 13), T(27, 14, 28, 14), T(32, 14, 33, 14), T(26, 13), T(34, 13), T(27, 20, 27, 22), T(33, 20, 33, 22), T(34, 23),
    # small meeting table; meeting 4 table, plants
    T(37, 16, 37, 21), T(41, 17, 42, 19), T(40, 14), T(40, 23), T(44, 23),
    # kitchen: counter row, island, dining table, standing table, plants, cabinet
    T(44, 1, 45, 8), T(48, 3, 48, 6), T(53, 5, 56, 5), T(55, 1, 57, 1), T(59, 2), T(59, 4, 59, 7),
    # large meeting: side table, plants, TV, table
    T(57, 12), T(59, 11), T(46, 23), T(59, 23), T(46, 16, 46, 20), T(48, 18, 58, 19),
]

# Open space: 4 long desk rows docked at the window wall, 3 seats on each side, desks on whole tiles with a free tile
# lane between the rows and along both walls. Chairs of neighbouring rows stay >= MIN_ROW_DISTANCE apart:
# WorkAdventure starts a conversation below MINIMUM_DISTANCE (35 px on this server), so seated neighbours never talk.
MIN_ROW_DISTANCE = 70
ROW_Y = (526, 610, 697)
DESK_ROWS = [[(x, y, f) for x, f in ((left, 'right'), (right, 'left')) for y in ROW_Y]
             for left, right in ((212, 298), (372, 458), (533, 618), (693, 780))]
OTHER_DESKS = [(94, 386, 'left'), (95, 501, 'left'), (95, 619, 'left'), (94, 730, 'left'),   # focus booths
               (918, 684, 'left'), (1036, 683, 'right'),                                      # phone rooms
               (939, 476, 'up'), (1013, 474, 'up')]                                          # reception

SEATS_PX = [s for r in DESK_ROWS for s in r] + OTHER_DESKS + [
    # lounge: two sofas (2 seats each), armchair, U couch (the couch itself is walkable)
    (113, 80, 'down'), (173, 80, 'down'), (113, 275, 'up'), (173, 275, 'up'), (392, 163, 'down'),
    (440, 106, 'down'), (472, 106, 'down'), (514, 110, 'down'), (514, 145, 'left'), (514, 180, 'left'),
    # small meeting: high table with 8 stools
    *[(1163, y, 'right') for y in (555, 595, 633, 673)], *[(1220, y, 'left') for y in (555, 595, 633, 673)],
    # meeting 4
    (1307, 568, 'right'), (1307, 620, 'right'), (1384, 568, 'left'), (1384, 620, 'left'),
    # kitchen: island stools, dining table, standing table
    (1599, 123, 'left'), (1599, 165, 'left'), (1599, 205, 'left'),
    (1712, 134, 'down'), (1749, 134, 'down'), (1787, 134, 'down'), (1712, 212, 'up'), (1749, 212, 'up'), (1787, 212, 'up'),
    (1792, 88, 'up'), (1832, 88, 'up'),
    # large meeting: 7 + 7 chairs, two armchairs next to the door
    *[(x, 547, 'down') for x in (1572, 1621, 1669, 1716, 1762, 1810, 1858)],
    *[(x, 650, 'up') for x in (1572, 1621, 1669, 1716, 1762, 1810, 1858)],
    (1815, 373, 'down'), (1880, 440, 'left'),
]

def px(t):
    """Tile rectangle -> pixel rectangle (end exclusive)."""
    return (t[0] * 32, t[1] * 32, (t[2] + 1) * 32, (t[3] + 1) * 32)

GONG_TILE = (25 * 32, 9 * 32)                      # gong drawn left of the coat rack
GONG = px(T(22, 9, 27, 11))                        # area in front of it: "space: hit the gong"
START = px(T(29, 6, 32, 7))                        # stair core, in front of the glass entrance door
SILENT = {"silentRestroom": px(T(19, 1, 24, 3)), "silentWomen": px(T(22, 5, 24, 7)), "silentMen": px(T(38, 1, 39, 7))}
CONF_ROOMS = [
    ("conference-big", "Large Meeting", px(T(46, 14, 59, 23))),
    ("conference-small", "Small Meeting", px(T(36, 14, 38, 23))),
    ("meeting-four", "Meeting 4", px(T(40, 14, 44, 23))),
    ("lounge", "Lounge", px(T(1, 1, 17, 8))),
]
MUST_REACH = {
    "kitchen": T(50, 7), "server": T(42, 4), "restroom": T(21, 2), "women": T(23, 6), "men": T(39, 4),
    "phone-left": T(28, 19), "phone-right": T(32, 19), "conference-big": T(52, 22), "conference-small": T(36, 22),
    "meeting-four": T(42, 22), "lounge": T(8, 3), "lounge-corner": T(16, 1),
    **{f"booth-{i}": T(3, y) for i, y in enumerate((10, 14, 17, 21))},
}
