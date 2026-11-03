#!/bin/sh
# Build the office map and upload it as the live map at the root of the map storage
# (START_ROOM_URL /~/elunic-office.wam, calendar on). There is no separate test map any more.
#
# The map storage upload DELETES EVERY FILE below the target directory, recursively (only some .wam files survive),
# before it unpacks the zip. That includes the custom entities people upload in the map editor
# (assets/entities/entities.json + images). So this script:
#   1. snapshots the complete live map storage (kubectl exec tar) and keeps a local copy in
#      .dream-loop/mapstorage-backups/<UTC timestamp>.tar,
#   2. builds the upload from that snapshot (everything we do not generate stays: assets/, other directories, ...)
#      plus our own files (map, script, tilesets, html, sound),
#   3. takes desk claims and editor-placed entities over from the live WAM (as long as the desk areas are unchanged),
#   4. after the upload checks that every snapshot file outside our own files still exists, and fails otherwise.
set -e
export LC_ALL=C   # sort and comm must agree on the order
cd "$(dirname "$0")"
python3 build_newoffice_art.py
NS=workadventure
MS="deploy/workadventure-mapstorage -c workadventure-mapstorage"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUPS=.dream-loop/mapstorage-backups
mkdir -p "$BACKUPS"
OUT=$(mktemp -d)
trap 'rm -rf "$OUT"' EXIT

# 1. snapshot of the live storage (lost+found and the storage's own cache file are not content)
kubectl -n $NS exec $MS -- tar -C /maps --exclude=./lost+found --exclude=./__cache.json -cf - . > "$BACKUPS/$STAMP.tar"
tar -tf "$BACKUPS/$STAMP.tar" | grep -v '/$' | sed 's|^\./||' | sort > "$OUT.before"
echo "snapshot: $(wc -l < "$OUT.before") files -> $BACKUPS/$STAMP.tar"
# the storage skips zip entries with a path part starting with "." but deletes them before unpacking: such files
# cannot survive an upload, so do not upload at all
HIDDEN=$(grep -E '(^|/)\.' "$OUT.before" || true)
if [ -n "$HIDDEN" ]; then
    echo "ERROR: these files would be lost by any upload (hidden path), move them first:"; echo "$HIDDEN"; exit 1
fi

# 2. start from the snapshot; our tilesets are replaced as a whole (old art versions would pile up otherwise)
tar -C "$OUT" -xf "$BACKUPS/$STAMP.tar"
rm -rf "$OUT/tilesets"
mkdir -p "$OUT/tilesets"
cp meeting-label.html meeting-chip.html gong.html elunic-gong.ogg "$OUT/"
python3 -c "
import json, shutil, sys
for t in json.load(open('newoffice.tmj'))['tilesets']: shutil.copy(t['image'], sys.argv[1] + '/' + t['image'])
" "$OUT"
NAME=elunic-office
sed -e 's/"newoffice\.wam"/"elunic-office.wam"/' -e 's/^const CALENDAR = false;/const CALENDAR = true;/' newoffice-script.js > "$OUT/elunic-desk-spawn.js"
grep -q '^const CALENDAR = true;' "$OUT/elunic-desk-spawn.js"
grep -q '"elunic-office.wam"' "$OUT/elunic-desk-spawn.js"
# 3. map files; the WAM keeps the live desk claims and entities
python3 - "$OUT" "$NAME" <<'PY'
import json, shutil, sys
out, name = sys.argv[1], sys.argv[2]
tmj = json.load(open('newoffice.tmj'))
for p in tmj['properties']:
    if p['name'] == 'mapImage': p['value'] = name + '.png'
    if p['name'] == 'mapDescription': p['value'] = 'elunic Buero, Erika-Mann-Str. 23, 6. OG'
    if p['name'] == 'mapName': p['value'] = 'elunic Buero'
json.dump(tmj, open(f'{out}/{name}.tmj', 'w'))
wam = json.load(open('newoffice.wam'))
wam['mapUrl'] = name + '.tmj'
live = json.load(open(f'{out}/{name}.wam'))          # from the snapshot, i.e. exactly what is live right now
if {a['id'] for a in live.get('areas', [])} == {a['id'] for a in wam['areas']}:
    wam['areas'] = live['areas']
else:
    print('desk areas changed: live claims are dropped')
wam['entities'] = live.get('entities', {})
print('live claims', sum(1 for a in wam['areas'] for q in a.get('properties', []) if q.get('ownerId')), 'entities', len(wam['entities']))
json.dump(wam, open(f'{out}/{name}.wam', 'w'), indent=1)
shutil.copy('newoffice.png', f'{out}/{name}.png')
PY
(cd "$OUT" && zip -q -r "$OUT.zip" .)

TOK=$(kubectl -n $NS get secret workadventure-secret-env-mapstorage -o jsonpath='{.data.AUTHENTICATION_TOKEN}' | base64 -d)
curl -s -o /dev/null -w 'upload %{http_code}\n' -H "Authorization: Bearer $TOK" -F "file=@$OUT.zip" \
    https://workadventure.starhunter.software/map-storage/upload
unset TOK

# 4. nothing that was there before may be missing (our tilesets excepted: they are replaced on purpose)
kubectl -n $NS exec $MS -- sh -c 'cd /maps && find . -type f ! -path "./lost+found/*" ! -name __cache.json' | sed 's|^\./||' | sort > "$OUT.after"
MISSING=$(grep -v '^tilesets/' "$OUT.before" | comm -23 - "$OUT.after")
rm -f "$OUT.before" "$OUT.after" "$OUT.zip"
if [ -n "$MISSING" ]; then
    echo "ERROR: files lost by the upload (restore from $BACKUPS/$STAMP.tar):"
    echo "$MISSING"
    exit 1
fi
echo "kept: all $(ls "$BACKUPS" | wc -l) snapshot(s) in $BACKUPS; no file lost"
