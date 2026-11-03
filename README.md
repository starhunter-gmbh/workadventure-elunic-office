# elunic office – WorkAdventure map

Maps of the elunic office for our WorkAdventure instance (`workadventure.starhunter.software`).

## Live: new office, Erika-Mann-Str. 23, 6th floor (since 2026-10-30)

Served at `/~/elunic-office.wam` (START_ROOM_URL). A painted map (Dream Loop target from the CSMM floor plan and the
walk-through video), not built from starter-kit tiles.

- `newoffice-art.png` – the painting (1952x800 px = 61x25 tiles); the tileset is this image cut into tiles
- `newoffice_spec.py` – gameplay data: hand-measured walls/furniture/doors on the tile grid, seats (pixel centres),
  rooms, silent zones, gong, start area
- `build_newoffice_art.py` – builds `newoffice.tmj/.wam/.png`, `newoffice-rooms.json` (calendar rooms, copied to
  `calendar/rooms.json` of wa-calendar in gitlab-ops-old-production-eu1-cluster) and `newoffice-script.js`
  (= `elunic-desk-spawn.js` with this map's seats and rooms); fails on unreachable seats/rooms or desk rows that are
  too close for the proximity chat
- `pack_newoffice.sh` – build + upload of the live map at the root (calendar on). The map storage deletes every
  file below the target directory before it unpacks a zip, including the custom entities uploaded in the map editor
  (`assets/entities/`). The script therefore snapshots the live storage first (local copy in
  `.dream-loop/mapstorage-backups/`), uploads that snapshot plus our files, keeps desk claims and editor entities, and
  fails if any file is missing afterwards. Never upload a zip to the map storage by hand.

## Previous map (old office, until 2026-10-30)

Rebuild of the old office (traced from the old Gather Town map).

- `elunic-office.tmj` – the map (Tiled JSON, 54x36 tiles, 32px)
- `elunic-office.png` – rendered preview
- `tilesets/` – WorkAdventure starter-kit tilesets (CC-BY-SA 3.0, see `LICENSE.assets`)
- `build.py` – generator; edit the layout there and run `python3 build.py .`
  (needs Pillow; `office.tmj` from the starter kit is the source of the furniture stamps)

Entrance: stairwell north of the reception (start area). Three balconies (left, right, bottom).
No Jitsi areas.
