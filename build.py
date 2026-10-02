"""Generate elunic-office.tmj (WorkAdventure) from starter-kit tilesets, layout traced from the old Gather map."""
import json, copy, sys
from PIL import Image

KIT = sys.argv[1] if len(sys.argv) > 1 else '.'
src = json.load(open(f'{KIT}/office.tmj'))
SW = src['width']
SRC = {}
def walk(ls):
    for l in ls:
        if l['type'] == 'group': walk(l['layers'])
        elif l['type'] == 'tilelayer': SRC[l['name']] = l['data']
walk(src['layers'])

W, H = 54, 36
LAYERS = ['floor1', 'floor2', 'walls1', 'walls2', 'furniture1', 'furniture2', 'furniture3', 'above1', 'above2', 'collisions', 'start']
L = {n: [0] * (W * H) for n in LAYERS}
def put(layer, x, y, g):
    if 0 <= x < W and 0 <= y < H: L[layer][y * W + x] = g
def get(layer, x, y): return L[layer][y * W + x]

# --- tile ids ---
GRASS, WOOD_LIGHT, WOOD_DARK, TILE_WHITE, SLATE, STONE, RED = 2461, 725, 752, 733, 735, 758, 762
COLL = 3
CUSTOM = 3000          # firstgid of tilesets/elunic_custom.png (see custom_tiles.py)
FLIP_Y = 0x40000000
FLIP_X = 0x80000000
KICKER, PINGPONG, TV, DART, SOFA_SIDE, URINAL = CUSTOM + 0, CUSTOM + 3, CUSTOM + 5, CUSTOM + 6, CUSTOM + 16, CUSTOM + 7
FACE = 603

def floor(x0, y0, x1, y1, g):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): put('floor1', x, y, g)

# --- base floors (coordinates traced 1:1 from the Gather screenshot grid) ---
floor(0, 0, W - 1, H - 1, GRASS)
floor(1, 13, 52, 31, SLATE)          # main building / open space
floor(14, 0, 24, 6, SLATE)           # conference room
floor(14, 6, 29, 18, WOOD_DARK)      # lounge / reception
floor(1, 8, 14, 13, STONE)           # left balcony
floor(37, 8, 52, 13, STONE)          # right balcony
floor(29, 12, 37, 18, TILE_WHITE); floor(37, 13, 41, 18, TILE_WHITE)  # WCs + server room
floor(41, 13, 45, 18, TILE_WHITE)    # kitchen
floor(45, 13, 52, 18, RED)           # red meeting room
floor(13, 14, 19, 18, SLATE)         # meeting room (incl. its door)
floor(39, 21, 52, 31, STONE)         # right offices (light grey)
floor(25, 31, 31, 33, STONE)         # bottom balcony
floor(25, 0, 29, 5, SLATE)           # stairwell (main entrance, north of reception)

WALL = set()
def hwall(x0, x1, y):
    for x in range(x0, x1 + 1): WALL.add((x, y))
def vwall(x, y0, y1):
    for y in range(y0, y1 + 1): WALL.add((x, y))
def door(*cells):
    for c in cells: WALL.discard(c)

# outer shell
hwall(14, 24, 0); vwall(14, 0, 13); vwall(24, 0, 6); hwall(24, 29, 6); vwall(29, 6, 12)
hwall(29, 37, 12); vwall(37, 12, 13)
hwall(1, 14, 13); hwall(37, 52, 13)
vwall(1, 13, 31); vwall(52, 13, 31); hwall(1, 25, 31); hwall(31, 52, 31)
# conference / lounge
hwall(14, 24, 6)
# meeting room below reception: own top wall towards the lounge
hwall(12, 20, 13)
# WC walls: towards lounge, towards server room, stall dividers
vwall(29, 12, 18); vwall(37, 12, 18)
vwall(31, 13, 13); vwall(35, 13, 13)          # stall dividers
hwall(31, 32, 16); hwall(34, 35, 16)           # wall between sink area and toilets, passage at 30 / 36
# front room row (bottom wall y18)
hwall(1, 20, 18); vwall(7, 13, 18); vwall(12, 13, 18); vwall(20, 13, 18)
hwall(29, 52, 18); vwall(33, 12, 18); vwall(41, 13, 18); vwall(45, 13, 18)
# right offices
hwall(39, 52, 21); vwall(39, 21, 31); vwall(47, 21, 31)
# right end of the open space: phone booth (1 person) and a small walled lounge-meeting corner
hwall(37, 38, 22); hwall(35, 38, 24); vwall(35, 24, 30); vwall(38, 24, 30)
# pillars in the open space
for px in (8, 15, 22): WALL.add((px, 22))

FENCE = set()
for x in range(1, 15): FENCE.add((x, 8))
for y in range(8, 14): FENCE.add((0, y))
for x in range(36, 54): FENCE.add((x, 8))
for y in range(8, 14): FENCE.add((53, y))
for y in range(8, 12): FENCE.add((36, y))   # right balcony, left edge
for x in range(24, 33): FENCE.add((x, 34))
for y in range(32, 35): FENCE.add((24, y)); FENCE.add((32, y))

# doors
hwall(24, 29, 0); vwall(29, 0, 6)       # stairwell walls
door((26, 6), (27, 6))                 # stairwell -> reception
door((22, 6))                 # conference <-> lounge
door((14, 11))               # lounge <-> left balcony
door((8, 13))                 # office B <-> balcony
door((4, 18), (9, 18), (13, 18))
door((20, 16))               # meeting <-> lounge
door((30, 18), (36, 18), (40, 18), (43, 18), (50, 18))
door((50, 13))               # red room <-> right balcony
door((45, 21), (49, 21))
door((35, 29))                         # small lounge entrance
door((27, 31), (28, 31))
for x in range(21, 29): WALL.discard((x, 18))   # lounge open towards corridor

def wall_tile(x, y):
    n, s, e, w = ((x, y - 1) in WALL, (x, y + 1) in WALL, (x + 1, y) in WALL, (x - 1, y) in WALL)
    table = {
        (1, 1, 0, 0): 477, (0, 0, 1, 1): 479, (0, 1, 1, 0): 403, (0, 1, 0, 1): 404,
        (1, 0, 1, 0): 428, (1, 0, 0, 1): 429, (0, 1, 1, 1): 535, (1, 0, 1, 1): 485,
        (1, 0, 0, 0): 431, (0, 1, 0, 0): 406, (0, 0, 1, 0): 440, (0, 0, 0, 1): 438,
        (1, 1, 1, 1): 512, (1, 1, 1, 0): 477, (1, 1, 0, 1): 477, (0, 0, 0, 0): 386,
    }
    return table[(int(n), int(s), int(e), int(w))]

for (x, y) in WALL:
    put('walls1', x, y, wall_tile(x, y)); put('collisions', x, y, COLL)
RAIL = 2500   # dark metal balcony railing (WA_Exterior)
for (x, y) in FENCE: put('collisions', x, y, COLL); put('walls2', x, y, RAIL)

inside = [[False] * W for _ in range(H)]
def mark(x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1): inside[y][x] = True
mark(1, 13, 52, 31); mark(14, 0, 29, 18); mark(1, 9, 14, 13); mark(37, 9, 52, 13)
mark(25, 0, 28, 5); mark(29, 12, 37, 13); mark(25, 31, 31, 33)
for y in range(H):
    for x in range(W):
        if not inside[y][x]: put('collisions', x, y, COLL)

# wall faces below horizontal walls inside rooms
for (x, y) in list(WALL):
    if wall_tile(x, y) in (479, 403, 404, 535, 440, 438) and (x, y + 1) not in WALL and y + 1 < H \
            and inside[y + 1][x] and y + 1 not in (19, 23) and get('floor1', x, y + 1) not in (STONE, GRASS):
        pass  # faces disabled: they ate the top row of every room

# --- stamps copied from the starter-kit office ---
FURN = ['furniture1', 'furniture2', 'furniture3', 'above1', 'above2']
def stamp(sx, sy, w, h, tx, ty, coll=True):
    for dy in range(h):
        for dx in range(w):
            i = (sy + dy) * SW + sx + dx
            any_t = False
            for n in FURN:
                g = SRC[n][i]
                if g: put(n, tx + dx, ty + dy, g); any_t = True
            if coll and any_t and SRC['collisions'][i]: put('collisions', tx + dx, ty + dy, COLL)

def stamp_onto(sx, sy, w, tx, ty, layer='furniture3'):
    """Copy one source row into a single higher layer, so it overlays what is already there."""
    for dx in range(w):
        i = sy * SW + sx + dx
        for n in FURN:
            if SRC[n][i]: put(layer, tx + dx, ty, SRC[n][i])
            if SRC['collisions'][i]: put('collisions', tx + dx, ty, COLL)

def obj(layer, x, y, g, coll=True):
    put(layer, x, y, g)
    if coll: put('collisions', x, y, COLL)

DESK4 = (10, 3, 4, 5)
DESK2 = (10, 3, 2, 5)        # one desk column + chairs on the left
LONGDESK = (12, 9, 6, 5)
COUNTER = (1, 7, 2, 6)
OUT_TABLE = (12, 18, 6, 2)
BENCHES = (21, 17, 5, 1)

def block(x, y, w, h, first, cols=8, flip=0, coll=True):
    """Place a w*h block from the custom tileset (index layout with `cols` columns)."""
    for dy in range(h):
        for dx in range(w):
            obj('furniture1', x + dx, y + dy, (first + dy * cols + dx) | flip, coll)
def plant_big(x, y):
    put('furniture2', x, y, 91); put('furniture1', x, y + 1, 103); put('collisions', x, y + 1, COLL)
def plant_small(x, y):
    obj('furniture1', x, y, 83)
def planter(x0, x1, y):
    for x in range(x0, x1 + 1): put('furniture1', x, y, 83)

# conference room: long table centred
for x in range(17, 22):
    put('furniture2', x, 1, 1497); put('furniture2', x, 2, 1510)        # chairs facing down
    put('furniture2', x, 4, 1499); put('furniture2', x, 5, 1512)        # chairs facing up
for x in range(16, 23):
    c = 0 if x == 16 else 3 if x == 22 else 1
    obj('furniture1', x, 3, 1567 + c)
stamp(10, 4, 1, 1, 15, 3, coll=False)                                   # chair at the left table end
for dy in range(3): obj('furniture1', 23, 2 + dy, (TV + dy * 8) | FLIP_X) # TV on the right wall
# lounge: plant, sofa + armchairs, curved reception desk, bar on the right
plant_big(15, 7)
stamp(2, 3, 4, 1, 16, 7)                       # sofa
stamp(1, 4, 1, 2, 16, 8); stamp(6, 5, 1, 1, 19, 8)
for x in range(16, 23):                        # reception counter, horizontal part
    obj('furniture1', x, 10, 1598); obj('furniture1', x, 11, 1608)
obj('furniture1', 16, 10, 1597); obj('furniture1', 16, 11, 1607)
for y, g in zip(range(10, 14), (1627, 1637, 1647, 1667)):   # reception counter, right wing of the L
    obj('furniture1', 23, y, g)
put('furniture2', 18, 10, 110); put('furniture2', 21, 10, 110)   # two workstations
stamp(10, 4, 1, 1, 18, 12, coll=False); stamp(10, 4, 1, 1, 21, 12, coll=False)
for y, g in zip(range(9, 15), (1627, 1637, 1647, 1647, 1657, 1667)):   # long table along the right wall
    obj('furniture1', 28, y, g)
block(22, 15, 2, 2, PINGPONG)
# left balcony
stamp(*OUT_TABLE, 7, 10)
plant_big(3, 11)
# right balcony: lounge set on the left, table for 8 on the right
for dx in range(4):                            # long sofa at the bottom, facing up
    for n in FURN:
        g = SRC[n][3 * SW + 2 + dx]
        if g: put(n, 39 + dx, 12, g | FLIP_Y)
stamp(1, 4, 1, 2, 38, 9)                       # armchair left
stamp(6, 5, 1, 1, 43, 10)                      # armchair right
stamp(3, 5, 2, 1, 40, 10)                      # coffee table
for i, g in enumerate([1567, 1568, 1569, 1570, 1577, 1578, 1579, 1580]):
    obj('furniture1', 46 + i % 4, 10 + i // 4, g)
for x in range(46, 50):
    put('furniture1', x, 9, 1525); put('furniture1', x, 12, 1525)   # seats
# office A / B
stamp(10, 3, 2, 3, 4, 14); stamp(10, 3, 2, 3, 9, 14)
# meeting room
stamp(12, 10, 6, 4, 13, 14)
# WCs: sink at the door, toilets behind the partition wall; men's (right) with 2 urinals on the left wall
for bx in (30, 34):
    obj('furniture1', bx, 13, 284); obj('furniture1', bx + 2, 13, 284)
put('furniture1', 34, 14, URINAL); put('furniture1', 34, 15, URINAL)   # men's = right WC
obj('furniture1', 32, 17, CUSTOM + 20)                                   # one sink per WC, against the side wall
obj('furniture1', 34, 17, CUSTOM + 19)
# server room: racks + admin desk
for y in (14, 15): obj('furniture1', 38, y, 133); obj('furniture1', 39, y, 134)
stamp(12, 4, 2, 2, 38, 16)
# kitchen: counter, coffee machine, fridge/printer cabinet
stamp(2, 8, 1, 4, 44, 14); obj('furniture1', 42, 14, 136); obj('furniture1', 42, 15, 146); obj('furniture1', 42, 17, 165)
# red meeting room
# dining room: long table, benches top / left / bottom, two spare chairs on the right wall, lane x50 free
for x, (t, b) in zip(range(47, 50), ((1557, 1577), (1558, 1578), (1560, 1580))):
    obj('furniture1', x, 15, t); obj('furniture1', x, 16, b)
for i, g in enumerate((1440, 1441, 1442)):
    put('furniture1', 47 + i, 14, g); put('furniture1', 47 + i, 17, g | FLIP_Y)
put('furniture1', 46, 15, CUSTOM + 14); put('furniture1', 46, 16, CUSTOM + 22)
stamp(13, 4, 1, 1, 51, 15, coll=False); stamp(13, 4, 1, 1, 51, 16, coll=False)
# open space: planters + desk clusters as in Gather
stamp(*DESK4, 11, 21); stamp(10, 4, 4, 4, 11, 26); stamp_onto(10, 3, 4, 11, 25)   # two blocks flush
stamp(*DESK4, 17, 21); stamp(10, 4, 4, 4, 17, 26); stamp_onto(10, 3, 4, 17, 25)   # two blocks flush
stamp(*DESK4, 23, 25)
stamp(*DESK4, 27, 25); stamp(*DESK4, 31, 25)
for x in (12, 13, 18, 19, 24, 25): put('above2', x, 21 if x < 20 else 25, CUSTOM + 15)   # planters flush on the desk edge, desk-wide
# white sideboard
for x in range(28, 34): obj('furniture1', x, 22, 1598); obj('furniture1', x, 23, 1608)

# left end of the open space: dart, kicker, TV with horseshoe couch, table tennis
block(4, 21, 3, 2, KICKER)
block(2, 26, 1, 3, TV)
for i, g in enumerate([1375, 1376, 1377, 1388, 1389, 1390]):          # top arm, facing down
    put('furniture1', 5 + i % 3, 24 + i // 3, g)
for i, g in enumerate([1388, 1389, 1390, 1375, 1376, 1377]):          # bottom arm, flipped to face up
    put('furniture1', 5 + i % 3, 28 + i // 3, g | FLIP_Y)
block(7, 24, 2, 3, SOFA_SIDE, coll=False)                             # back of the U, closing both corners
block(7, 27, 2, 3, SOFA_SIDE, coll=False)
for y, g in zip(range(24, 30), (1627, 1637, 1647, 1647, 1657, 1667)):   # long high table along the couch, with laptops
    obj('furniture1', 9, y, g)
for y in (25, 28): put('furniture2', 9, y, 132)
plant_big(2, 29)

# right end of the open space: printer, phone booth, small lounge with two 2-seaters
obj('furniture1', 38, 21, 146)   # printer, one tile so the corridor stays free
put('furniture1', 38, 23, 1471); put('furniture2', 38, 23, 110)       # booth: seat + screen
for i, g in enumerate([1405, 1406, 1418, 1419]):
    put('furniture1', 36 + i % 2, 25 + i // 2, g)
stamp(3, 5, 2, 1, 36, 27, coll=False)                                  # coffee table
for i, g in enumerate([1418, 1419, 1405, 1406]):
    put('furniture1', 36 + i % 2, 28 + i // 2, g | FLIP_Y)
# right offices
stamp(12, 9, 2, 5, 41, 25); stamp(16, 9, 2, 5, 43, 25)
# rightmost office: desk bottom-left at the wall, small meeting table right-centre, cabinet above it
stamp(12, 3, 2, 3, 48, 28)
for (x, y), g in zip([(50, 25), (51, 25), (50, 26), (51, 26)], (1567, 1570, 1577, 1580)): obj('furniture1', x, y, g)
stamp(10, 4, 1, 1, 49, 25, coll=False)                                 # chair left of the table
put('furniture2', 50, 26, 1499); put('furniture2', 50, 27, 1512)       # chair below the table
for i, g in enumerate([233, 234, 245, 246]): obj('furniture1', 50 + i % 2, 22 + i // 2, g)
for x0 in (40, 42):                                                  # cabinets against the wall
    for i, g in enumerate([233, 234, 245, 246]): obj('furniture1', x0 + i % 2, 22 + i // 2, g)
# entrance
plant_big(25, 32); plant_big(31, 32)

for x in (26, 27): put('start', x, 4, 2); put('start', x, 5, 2)
for i, g in enumerate([827, 828, 829, 852, 853, 854]):   # staircase
    obj('furniture1', 25 + i % 3, 1 + i // 3, g)
plant_big(28, 3)

# --- assemble tmj ---
def tl(name, i):
    return {"data": L[name], "height": H, "width": W, "id": i, "name": name, "opacity": 1, "type": "tilelayer",
            "visible": True, "x": 0, "y": 0}

lid = [1]
def nid():
    lid[0] += 1; return lid[0]

def area(name, x, y, w, h, props):
    return {"height": h * 32, "width": w * 32, "x": x * 32, "y": y * 32, "id": nid(), "name": name, "rotation": 0,
            "type": "area", "visible": True,
            "properties": [{"name": k, "type": ("bool" if isinstance(v, bool) else "float" if isinstance(v, float) else "string"), "value": v} for k, v in props]}

objs = [
    area("silentWC1", 30, 13, 3, 5, [("silent", True)]),
    area("silentWC2", 34, 13, 3, 5, [("silent", True)]),
    area("start", 26, 4, 2, 2, [("start", True)]),
]

layers = [tl('start', nid()), tl('collisions', nid()),
          {"id": nid(), "name": "floor", "type": "group", "opacity": 1, "visible": True, "x": 0, "y": 0, "layers": [tl('floor1', nid()), tl('floor2', nid())]},
          {"id": nid(), "name": "walls", "type": "group", "opacity": 1, "visible": True, "x": 0, "y": 0, "layers": [tl('walls1', nid()), tl('walls2', nid())]},
          {"id": nid(), "name": "furniture", "type": "group", "opacity": 1, "visible": True, "x": 0, "y": 0, "layers": [tl('furniture1', nid()), tl('furniture2', nid()), tl('furniture3', nid())]},
          {"id": nid(), "name": "floorLayer", "type": "objectgroup", "draworder": "topdown", "opacity": 1, "visible": True, "x": 0, "y": 0, "objects": objs},
          {"id": nid(), "name": "above", "type": "group", "opacity": 1, "visible": True, "x": 0, "y": 0, "layers": [tl('above1', nid()), tl('above2', nid())]}]

for l in layers:
    if l['name'] == 'collisions': l['visible'] = False; l['opacity'] = 0.6
# start layer flagged via tile property in WA_Special_Zones? use property on layer instead
for l in layers:
    if l['name'] == 'start':
        l['properties'] = [{"name": "startLayer", "type": "bool", "value": True}]

out = copy.deepcopy(src)
src['tilesets'].append({'firstgid': CUSTOM, 'name': 'elunic_custom', 'image': 'tilesets/elunic_custom.png', 'imageheight': 160, 'imagewidth': 256, 'columns': 8, 'tilecount': 40, 'tileheight': 32, 'tilewidth': 32, 'margin': 0, 'spacing': 0})
out['tilesets'] = src['tilesets']
out.update(width=W, height=H, layers=layers, nextlayerid=lid[0] + 1, nextobjectid=lid[0] + 1)
out['properties'] = [
    {"name": "mapCopyright", "type": "string", "value": "Tilesets: WorkAdventure (https://workadventu.re), CC-BY-SA 3.0"},
    {"name": "mapDescription", "type": "string", "value": "elunic Buero, nachgebaut nach der alten Gather-Town-Map"},
    {"name": "mapName", "type": "string", "value": "elunic Buero"},
    {"name": "mapImage", "type": "string", "value": "elunic-office.png"},
]
json.dump(out, open(f'{KIT}/elunic-office.tmj', 'w'))

# --- preview render ---
img = Image.new('RGBA', (W * 32, H * 32), (0, 0, 0, 255))
ts = []
for t in out['tilesets']:
    ts.append((t['firstgid'], t['columns'], Image.open(f"{KIT}/{t['image']}").convert('RGBA')))
ts.sort()
cache = {}
def tile(g):
    if g & FLIP_Y: return tile(g & ~FLIP_Y).transpose(Image.FLIP_TOP_BOTTOM)
    if g & FLIP_X: return tile(g & ~FLIP_X).transpose(Image.FLIP_LEFT_RIGHT)
    g &= 0x1FFFFFFF
    if g in cache: return cache[g]
    for first, cols, im in reversed(ts):
        if g >= first:
            i = g - first; c = im.crop(((i % cols) * 32, (i // cols) * 32, (i % cols) * 32 + 32, (i // cols) * 32 + 32)); cache[g] = c; return c
for n in ['floor1', 'floor2', 'walls1', 'walls2', 'furniture1', 'furniture2', 'furniture3', 'above1', 'above2']:
    for y in range(H):
        for x in range(W):
            g = L[n][y * W + x]
            if g: img.alpha_composite(tile(g), (x * 32, y * 32))
img.convert('RGB').save(f'{KIT}/elunic-office.png')
print('ok', len(WALL))

# --- sanity checks: furniture on walls, unreachable floor ---
def check():
    issues = []
    for (x, y) in WALL:
        for n in FURN:
            if get(n, x, y): issues.append(f'furniture {n} on wall at {x},{y}')
    for y in range(H):
        for x in range(W):
            if get('walls2', x, y) == FACE and any(get(n, x, y) for n in FURN):
                issues.append(f'furniture on wall face at {x},{y}')
    from collections import deque
    start = [(x, y) for y in range(H) for x in range(W) if get('start', x, y)]
    seen = set(start); q = deque(start)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and not get('collisions', nx, ny):
                seen.add((nx, ny)); q.append((nx, ny))
    unreach = [(x, y) for y in range(H) for x in range(W) if inside[y][x] and not get('collisions', x, y) and (x, y) not in seen]
    return issues, unreach
issues, unreach = check()
print('\n'.join(issues)); print('unreachable', len(unreach), sorted(unreach, key=lambda c: (c[1], c[0])))
