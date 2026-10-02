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
floor(13, 14, 19, 17, SLATE)         # meeting room
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
vwall(31, 13, 14); vwall(35, 13, 14)
# front room row (bottom wall y18)
hwall(1, 20, 18); vwall(7, 13, 18); vwall(12, 13, 18); vwall(20, 13, 18)
hwall(29, 52, 18); vwall(33, 12, 18); vwall(41, 13, 18); vwall(45, 13, 18)
# right offices
hwall(39, 52, 21); vwall(39, 21, 31); vwall(47, 21, 31)
# pillars in the open space
for px in (8, 15, 22): WALL.add((px, 22))

FENCE = set()
for x in range(1, 15): FENCE.add((x, 8))
for y in range(8, 14): FENCE.add((0, y))
for x in range(36, 54): FENCE.add((x, 8))
for y in range(8, 14): FENCE.add((53, y))
for y in range(8, 12): FENCE.add((36, y))   # right balcony, left edge
for x in range(24, 33): FENCE.add((x, 34))
for y in range(31, 35): FENCE.add((24, y)); FENCE.add((32, y))

# doors
hwall(24, 29, 0); vwall(29, 0, 6)       # stairwell walls
door((26, 6), (27, 6))                 # stairwell -> reception
door((21, 6), (22, 6))                 # conference <-> lounge
door((14, 11), (14, 12))               # lounge <-> left balcony
door((8, 13), (9, 13))                 # office B <-> balcony
door((4, 18), (5, 18), (9, 18), (13, 18), (14, 18))
door((20, 15), (20, 16))               # meeting <-> lounge
door((30, 18), (36, 18), (39, 18), (40, 18), (43, 18), (50, 18))
door((49, 13), (50, 13))               # red room <-> right balcony
door((45, 21), (46, 21), (50, 21))
door((26, 31), (27, 31), (28, 31), (29, 31), (30, 31))
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
        put('walls2', x, y + 1, FACE)

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

def obj(layer, x, y, g, coll=True):
    put(layer, x, y, g)
    if coll: put('collisions', x, y, COLL)

DESK4 = (10, 3, 4, 5)
DESK2 = (10, 3, 2, 5)        # one desk column + chairs on the left
LONGDESK = (12, 9, 6, 5)
COUNTER = (1, 7, 2, 6)
OUT_TABLE = (12, 18, 6, 2)
BENCHES = (21, 17, 5, 1)

def plant_big(x, y):
    put('furniture2', x, y, 91); put('furniture1', x, y + 1, 103); put('collisions', x, y + 1, COLL)
def plant_small(x, y):
    obj('furniture1', x, y, 83)
def planter(x0, x1, y):
    for x in range(x0, x1 + 1): obj('furniture1', x, y, 83)

# conference room: long table centred
stamp(*LONGDESK, 16, 1); plant_big(15, 1)
# lounge: plant, sofa + armchairs, curved reception desk, bar on the right
plant_big(15, 6)
stamp(2, 3, 4, 1, 16, 7)                       # sofa
stamp(1, 4, 1, 2, 16, 8); stamp(6, 5, 1, 1, 19, 8)
for x in range(16, 23):                        # reception counter, horizontal part
    obj('furniture1', x, 10, 1598); obj('furniture1', x, 11, 1608)
obj('furniture1', 16, 10, 1597); obj('furniture1', 16, 11, 1607)
for y in range(10, 13):                        # reception counter, curved right wing
    obj('furniture1', 23, y, 1598 if y < 12 else 1608)
put('furniture2', 18, 10, 110)                 # monitor
stamp(10, 4, 1, 1, 18, 12, coll=False); stamp(10, 4, 1, 1, 21, 12, coll=False)
stamp(*COUNTER, 27, 12)                        # bar
plant_small(28, 10)
# left balcony
stamp(*OUT_TABLE, 7, 10)
plant_big(3, 11)
# right balcony: lounge set on the left, table for 8 on the right
stamp(2, 3, 4, 1, 39, 9)                       # sofa
stamp(1, 4, 1, 2, 38, 10)                      # armchair left
stamp(6, 5, 1, 1, 43, 11)                      # armchair right
stamp(3, 5, 2, 1, 40, 11)                      # coffee table
for i, g in enumerate([1567, 1568, 1569, 1570, 1577, 1578, 1579, 1580]):
    obj('furniture1', 46 + i % 4, 10 + i // 4, g)
for x in range(46, 50):
    put('furniture1', x, 9, 1525); put('furniture1', x, 12, 1525)   # seats
# office A / B
stamp(10, 3, 2, 3, 4, 14); stamp(10, 3, 2, 3, 9, 14)
# meeting room
stamp(12, 10, 6, 4, 13, 14)
# WCs
for bx in (30, 34):
    obj('furniture1', bx, 13, 284); obj('furniture1', bx + 1, 13, 284); obj('furniture1', bx + 2, 15, 283)
# server room: racks + admin desk
for y in (14, 15, 16): obj('furniture1', 38, y, 133); obj('furniture1', 39, y, 134)
stamp(10, 3, 2, 3, 39, 15)
# kitchen: counter, coffee machine, fridge/printer cabinet
stamp(*COUNTER, 42, 13); obj('furniture1', 44, 14, 165); obj('furniture1', 44, 15, 136); obj('furniture1', 44, 16, 146)
# red meeting room
plant_big(46, 14); stamp(*DESK4, 47, 14)
# open space: planters + desk clusters as in Gather
planter(10, 13, 22); planter(17, 19, 22); planter(25, 27, 24)
stamp(*DESK4, 11, 23); stamp(*DESK4, 11, 27)
stamp(*DESK4, 17, 23); stamp(*DESK4, 17, 27)
stamp(*DESK4, 24, 25)
stamp(*DESK4, 29, 25); stamp(*DESK4, 33, 25)
# white sideboard + games corner
for x in range(28, 35): obj('furniture1', x, 22, 1598); obj('furniture1', x, 23, 1608)
stamp(*OUT_TABLE, 2, 20)                       # kicker placeholder
obj('furniture1', 7, 26, 1561); obj('furniture1', 8, 26, 1562); obj('furniture1', 7, 27, 1571); obj('furniture1', 8, 27, 1572)  # table tennis placeholder
for i, g in enumerate([241, 242, 253, 254, 265, 266]):
    obj('furniture1', 2 + i % 2, 25 + i // 2, g)
plant_big(2, 29); plant_small(2, 23)
for i, g in enumerate([241, 242, 253, 254, 265, 266]):
    obj('furniture1', 37 + i % 2, 25 + i // 2, g)
# right offices
stamp(*DESK4, 41, 25)
stamp(10, 3, 2, 3, 49, 24); stamp(10, 3, 2, 3, 48, 27)
for x in range(40, 44): obj('furniture1', x, 22, 1598)
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
