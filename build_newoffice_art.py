"""Generate newoffice.tmj from a painted map image (Dream Loop target, .dream-loop/newoffice) instead of starter-kit tiles.

The art (newoffice-art.png, a multiple of 32 px in both directions) is cut into a tileset that is placed 1:1 as the
floor layer. Walls are detected from the dark wall colour per tile; furniture collisions, seats and rooms come from
newoffice_spec.py (pixel coordinates in the art). Output: newoffice.tmj / .wam / -rooms.json / -script.js / .png.
"""
import json, math, re, uuid, hashlib, glob, os, shutil, sys
from PIL import Image
import newoffice_spec as S

KIT = '.'
art = Image.open(S.ART).convert('RGBA')
# the gong (elunic_custom tile 42) is not part of the painting: draw it into the corridor
gong = Image.open('tilesets/elunic_custom.png').convert('RGBA').crop((2 * 32, 5 * 32, 3 * 32, 6 * 32))
art.alpha_composite(gong, S.GONG_TILE)
assert art.width % 32 == 0 and art.height % 32 == 0, art.size
W, H = art.width // 32, art.height // 32

# --- tileset: the art itself, content-hashed file name (the map storage rejects query strings in tileset paths) ---
ver = hashlib.md5(art.tobytes()).hexdigest()[:8]
for old in glob.glob(f'{KIT}/tilesets/newoffice-art-*.png'):
    if not old.endswith(f'-{ver}.png'): os.remove(old)
art_path = f'tilesets/newoffice-art-{ver}.png'
art.save(f'{KIT}/{art_path}')
ART_FIRST = 1
SPECIAL_FIRST = ART_FIRST + W * H        # WA_Special_Zones for the collision / start markers
COLL = SPECIAL_FIRST + 2
START = SPECIAL_FIRST + 1

# --- collisions: hand-measured tile rectangles (newoffice_spec.py); doors and seat tiles are walkable ---
coll = [[False] * W for _ in range(H)]
def cells(t):
    for ty in range(t[1], t[3] + 1):
        for tx in range(t[0], t[2] + 1): yield tx, ty
for t in S.WALLS + S.BLOCK:
    for tx, ty in cells(t): coll[ty][tx] = True
for t in S.DOORS:
    for tx, ty in cells(t): coll[ty][tx] = False
for x, y, _d in S.SEATS_PX:
    coll[y // 32][x // 32] = False
def tiles_of(rect):
    x0, y0, x1, y1 = rect                                                       # pixels, end exclusive
    for ty in range(max(0, y0 // 32), min(H, (y1 - 1) // 32 + 1)):
        for tx in range(max(0, x0 // 32), min(W, (x1 - 1) // 32 + 1)):
            yield tx, ty
seat_tiles = [(x // 32, y // 32) for x, y, _d in S.SEATS_PX]
dup = {t for t in seat_tiles if seat_tiles.count(t) > 1}
assert not dup, f'two seats on one tile: {sorted(dup)}'

# preview with collisions tinted, for checking
prev = art.copy()
ov = Image.new('RGBA', art.size, (0, 0, 0, 0))
for y in range(H):
    for x in range(W):
        if coll[y][x]: ov.paste((255, 0, 0, 70), (x * 32, y * 32, x * 32 + 32, y * 32 + 32))
for x, y, _d in S.SEATS_PX: ov.paste((0, 255, 0, 200), (x - 4, y - 4, x + 4, y + 4))
prev.alpha_composite(ov); prev.convert('RGB').save(f'{KIT}/.dream-loop/newoffice/collisions.png')
# --- reachability check from the start area ---
from collections import deque
start = [(tx, ty) for tx, ty in tiles_of(S.START)]
seen = set(start); q = deque(start)
while q:
    x, y = q.popleft()
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in seen and not coll[ny][nx]:
            seen.add((nx, ny)); q.append((nx, ny))
unreach_seats = [(x, y) for x, y, _d in S.SEATS_PX if (x // 32, y // 32) not in seen]
assert not unreach_seats, f'unreachable seats: {unreach_seats}'
unreach_rooms = [name for name, t in S.MUST_REACH.items() if not any(c in seen for c in cells(t))]
assert not unreach_rooms, f'unreachable rooms: {unreach_rooms}'

# --- open space: chairs of neighbouring desk rows must stay far apart (MINIMUM_DISTANCE 35 px, GROUP_RADIUS 48 px) ---
rows = S.DESK_ROWS
min_px = min(math.hypot(a[0] - b[0], a[1] - b[1]) for i, r1 in enumerate(rows) for r2 in rows[i + 1:] for a in r1 for b in r2)
assert min_px >= S.MIN_ROW_DISTANCE, f'desk rows too close: {min_px:.0f}px'
same_row = min(math.hypot(a[0] - b[0], a[1] - b[1]) for r in rows for i, a in enumerate(r) for b in r[i + 1:])
print(f'open space: {len(rows)} rows x {[len(r) for r in rows]} chairs, between rows >= {min_px:.0f}px, within a row >= {same_row:.0f}px')

# --- tmj ---
lid = [1]
def nid():
    lid[0] += 1; return lid[0]
def tl(name, data):
    return {"data": data, "height": H, "width": W, "id": nid(), "name": name, "opacity": 1, "type": "tilelayer",
            "visible": True, "x": 0, "y": 0}
floor = [ART_FIRST + i for i in range(W * H)]
collisions = [COLL if coll[y][x] else 0 for y in range(H) for x in range(W)]
startl = [0] * (W * H)
for tx, ty in tiles_of(S.START): startl[ty * W + tx] = START
def area(name, rect, props):
    x0, y0, x1, y1 = rect
    return {"height": y1 - y0, "width": x1 - x0, "x": x0, "y": y0, "id": nid(), "name": name, "rotation": 0,
            "type": "area", "visible": True,
            "properties": [{"name": k, "type": ("bool" if isinstance(v, bool) else "string"), "value": v} for k, v in props]}
objs = [area(n, r, [("silent", True)]) for n, r in S.SILENT.items()] + [area("start", S.START, [("start", True)])]
cl = tl('collisions', collisions); cl['visible'] = False; cl['opacity'] = 0.6
st = tl('start', startl); st['properties'] = [{"name": "startLayer", "type": "bool", "value": True}]
layers = [st, cl,
          {"id": nid(), "name": "floor", "type": "group", "opacity": 1, "visible": True, "x": 0, "y": 0, "layers": [tl('floor1', floor)]},
          {"id": nid(), "name": "floorLayer", "type": "objectgroup", "draworder": "topdown", "opacity": 1, "visible": True, "x": 0, "y": 0, "objects": objs}]
tilesets = [
    {'firstgid': ART_FIRST, 'name': 'newoffice_art', 'image': art_path, 'imagewidth': art.width, 'imageheight': art.height,
     'columns': W, 'tilecount': W * H, 'tilewidth': 32, 'tileheight': 32, 'margin': 0, 'spacing': 0},
    {'firstgid': SPECIAL_FIRST, 'name': 'WA_Special_Zones', 'image': 'tilesets/WA_Special_Zones.png', 'imagewidth': 192, 'imageheight': 64,
     'columns': 6, 'tilecount': 12, 'tilewidth': 32, 'tileheight': 32, 'margin': 0, 'spacing': 0,
     'tiles': [{'id': 2, 'properties': [{'name': 'collides', 'type': 'bool', 'value': True}]}]},
]
tmj = {"compressionlevel": -1, "infinite": False, "orientation": "orthogonal", "renderorder": "right-down", "type": "map",
       "version": "1.10", "tiledversion": "1.10.2", "tilewidth": 32, "tileheight": 32, "width": W, "height": H,
       "nextlayerid": lid[0] + 1, "nextobjectid": lid[0] + 1, "layers": layers, "tilesets": tilesets,
       "properties": [
           {"name": "mapCopyright", "type": "string", "value": "elunic, generated artwork"},
           {"name": "mapDescription", "type": "string", "value": "elunic Buero, Erika-Mann-Str. 23, 6. OG (Testkarte)"},
           {"name": "mapName", "type": "string", "value": "elunic Buero (neu)"},
           {"name": "mapImage", "type": "string", "value": "newoffice.png"},
           {"name": "script", "type": "string", "value": "elunic-desk-spawn.js"},   # the play bridges only trust this file name
       ]}
json.dump(tmj, open(f'{KIT}/newoffice.tmj', 'w'))

art.convert('RGB').save(f'{KIT}/newoffice.png')

# --- WAM: every desk seat is a claimable personal area ---
NS = uuid.UUID('6f0f3c1e-2a7b-4c1e-9d4a-0e1c00000002')
def seat_area(i, x, y):
    return {"id": str(uuid.uuid5(NS, f"seat-{i}")), "x": x - 24, "y": y - 24, "width": 48, "height": 48,
            "visible": True, "name": f"Arbeitsplatz {i + 1}",
            "properties": [{"id": str(uuid.uuid5(NS, f"seat-prop-{i}")), "type": "personalAreaPropertyData",
                            "accessClaimMode": "dynamic", "allowedTags": [], "ownerId": None}]}
desks = [c for r in S.DESK_ROWS for c in r] + S.OTHER_DESKS
wam = {"version": "1.0.0", "mapUrl": "newoffice.tmj", "entities": {},
       "areas": [seat_area(i, x, y) for i, (x, y, _d) in enumerate(desks)],
       "entityCollections": [{"url": "https://workadventure.starhunter.software/collections/FurnitureCollection.json", "type": "file"},
                             {"url": "https://workadventure.starhunter.software/collections/OfficeCollection.json", "type": "file"}],
       "metadata": {"name": "elunic Buero (neu)", "description": "elunic Buero Erika-Mann-Str. 23 mit beanspruchbaren Arbeitsplaetzen"}}
json.dump(wam, open(f'{KIT}/newoffice.wam', 'w'), indent=1)
spawns = {a["id"]: list(d) for a, d in zip(wam["areas"], desks)}

# --- rooms for the calendar service (elunic-rooms.json format; not wired up while this is a test map) ---
rooms = []
for rid, label, rect in S.CONF_ROOMS:
    x0, y0, x1, y1 = rect
    seats = [[x, y] for x, y, _d in S.SEATS_PX if x0 <= x < x1 and y0 <= y < y1]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    standing = sorted(([tx * 32 + 16, ty * 32 + 16] for tx, ty in tiles_of(rect) if not coll[ty][tx]
                       and all(math.hypot(tx * 32 + 16 - s[0], ty * 32 + 16 - s[1]) > 20 for s in seats)),
                      key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
    rooms.append({"id": rid, "label": label, "seats": seats, "standing": standing})
json.dump({"rooms": rooms}, open(f'{KIT}/newoffice-rooms.json', 'w'), indent=1)
print('rooms', [(r["id"], len(r["seats"]), len(r["standing"])) for r in rooms])

# --- map script: same behaviour as elunic-desk-spawn.js with this map's chairs, rooms and gong; no calendar pings ---
js = open(f'{KIT}/elunic-desk-spawn.js').read()
js = re.sub(r'^const SPAWNS = .*$', lambda m: 'const SPAWNS = ' + json.dumps(spawns) + ';', js, count=1, flags=re.M)
js = re.sub(r'^const CHAIRS = .*$', lambda m: 'const CHAIRS = ' + json.dumps([list(s) for s in S.SEATS_PX]) + ';', js, count=1, flags=re.M)
js = re.sub(r'^const ROOM_RECTS = .*$', lambda m: 'const ROOM_RECTS = ' + json.dumps(
    {rid: [x0, y0, x1 - x0, y1 - y0] for rid, _l, (x0, y0, x1, y1) in S.CONF_ROOMS}) + ';', js, count=1, flags=re.M)
js = js.replace('"elunic-office.wam"', '"newoffice.wam"')
gx0, gy0, gx1, gy1 = S.GONG
js = js.replace('x: 40 * 32, y: 19 * 32, width: 5 * 32, height: 2 * 32', f'x: {gx0}, y: {gy0}, width: {gx1 - gx0}, height: {gy1 - gy0}')
js = js.replace('deskSpawnDone.catch(() => {}).then(tick);', 'if (CALENDAR) deskSpawnDone.catch(() => {}).then(tick);')
js = js.replace('setInterval(tick, 30000);', 'if (CALENDAR) setInterval(tick, 30000);')
js = js.replace('const SPAWNS = ', '// Test map: no calendar pings (wa-calendar still assigns seats of the live map).\nconst CALENDAR = false;\nconst SPAWNS = ', 1)
for needle in ('"newoffice.wam"', f'x: {gx0}, y: {gy0}', 'if (CALENDAR) deskSpawnDone', 'if (CALENDAR) setInterval'):
    assert needle in js, needle
open(f'{KIT}/newoffice-script.js', 'w').write(js)
print(f'map {W}x{H} tiles, seats {len(S.SEATS_PX)}, claimable desks {len(desks)}')
