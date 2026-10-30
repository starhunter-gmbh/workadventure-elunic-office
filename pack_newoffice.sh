#!/bin/sh
# Build the new office map and upload it to the map storage.
#   ./pack_newoffice.sh        test map, directory "neuesbuero" (https://workadventure.starhunter.software/~/neuesbuero/newoffice.wam),
#                              calendar pings off
#   ./pack_newoffice.sh live   the live office map at the root (START_ROOM_URL /~/elunic-office.wam), calendar on.
#                              Replaces elunic-office.wam: desk claims of the previous map are dropped.
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
if [ "$1" = live ]; then
    NAME=elunic-office DIR=
    sed -e 's/"newoffice\.wam"/"elunic-office.wam"/' -e 's/^const CALENDAR = false;/const CALENDAR = true;/' newoffice-script.js > "$OUT/elunic-desk-spawn.js"
    grep -q '^const CALENDAR = true;' "$OUT/elunic-desk-spawn.js"
    grep -q '"elunic-office.wam"' "$OUT/elunic-desk-spawn.js"
else
    NAME=newoffice DIR=neuesbuero
    cp newoffice-script.js "$OUT/elunic-desk-spawn.js"   # the play image's seat/status bridges only trust this file name
fi
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
json.dump(wam, open(f'{out}/{name}.wam', 'w'), indent=1)
shutil.copy('newoffice.png', f'{out}/{name}.png')
PY
(cd "$OUT" && zip -q -r map.zip .)
TOK=$(kubectl -n workadventure get secret workadventure-secret-env-mapstorage -o jsonpath='{.data.AUTHENTICATION_TOKEN}' | base64 -d)
curl -s -o /dev/null -w 'upload %{http_code}\n' -H "Authorization: Bearer $TOK" -F "file=@$OUT/map.zip" ${DIR:+-F "directory=$DIR"} \
    https://workadventure.starhunter.software/map-storage/upload
unset TOK
rm -rf "$OUT"
