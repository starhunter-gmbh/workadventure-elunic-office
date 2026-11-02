#!/bin/sh
# Build the office map and upload it as the live map at the root of the map storage
# (START_ROOM_URL /~/elunic-office.wam, calendar on). There is no separate test map any more.
# Desk claims and entities placed in the map editor are taken over from the live WAM as long as the desk areas are
# unchanged (same ids); otherwise the claims are dropped.
# The map storage upload REPLACES every file of the target directory (subdirectories stay): always upload the complete
# package, never a single file.
set -e
cd "$(dirname "$0")"
python3 build_newoffice_art.py
OUT=$(mktemp -d)
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
python3 - "$OUT" "$NAME" <<'PY'
import json, shutil, sys
out, name = sys.argv[1], sys.argv[2]
tmj = json.load(open('newoffice.tmj'))
for p in tmj['properties']:
    if p['name'] == 'mapImage': p['value'] = name + '.png'
    if name == 'elunic-office' and p['name'] == 'mapDescription': p['value'] = 'elunic Buero, Erika-Mann-Str. 23, 6. OG'
    if name == 'elunic-office' and p['name'] == 'mapName': p['value'] = 'elunic Buero'
json.dump(tmj, open(f'{out}/{name}.tmj', 'w'))
wam = json.load(open('newoffice.wam'))
wam['mapUrl'] = name + '.tmj'
if name == 'elunic-office':
    import urllib.request
    live = json.load(urllib.request.urlopen('https://workadventure.starhunter.software/map-storage/elunic-office.wam'))
    if {a['id'] for a in live.get('areas', [])} == {a['id'] for a in wam['areas']}:
        wam['areas'] = live['areas']
    else:
        print('desk areas changed: live claims are dropped')
    wam['entities'] = live.get('entities', {})
    print('live claims', sum(1 for a in wam['areas'] for q in a.get('properties', []) if q.get('ownerId')), 'entities', len(wam['entities']))
json.dump(wam, open(f'{out}/{name}.wam', 'w'), indent=1)
shutil.copy('newoffice.png', f'{out}/{name}.png')
PY
(cd "$OUT" && zip -q -r map.zip .)
TOK=$(kubectl -n workadventure get secret workadventure-secret-env-mapstorage -o jsonpath='{.data.AUTHENTICATION_TOKEN}' | base64 -d)
curl -s -o /dev/null -w 'upload %{http_code}\n' -H "Authorization: Bearer $TOK" -F "file=@$OUT/map.zip" \
    https://workadventure.starhunter.software/map-storage/upload
unset TOK
rm -rf "$OUT"
