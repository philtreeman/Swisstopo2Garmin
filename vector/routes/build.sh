#!/bin/bash
# Baut 6 Overlay-Karten, jede als eigene .img-Datei (eigene Family-ID, eigener TYP):
#   wanderwege, wanderland, veloland, mountainbike, skirouten_blau, skirouten_schwierigkeit
#   routes/build.sh <daten-ordner> <mkgmap.jar> <out-ordner> [W S E N]
# <daten-ordner> enthaelt: SWISSTLM3D_WANDERWEGE.gpkg wanderland.gpkg veloland.gpkg
#                          mountainbikeland.gpkg ski_routes_2056.gpkg
# Ergebnis: <out>/swisstopo_<name>.img. Ohne Bounding Box: ganze Schweiz (gross).
set -e
D=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
V=$(cd "$(dirname "$0")/.." && pwd)
# Kacheln: mit Bounding Box eine Kachel; ohne Bounding Box die ganze Schweiz in 2x2 Kacheln
if [ $# -eq 4 ]; then TILES=("$1 $2 $3 $4")
else TILES=("5.90 45.80 8.25 46.85" "8.25 45.80 10.60 46.85" "5.90 46.85 8.25 47.85" "8.25 46.85 10.60 47.85"); fi
mkdir -p "$OUT/osm"
conv() {  # conv <kind> <gpkg>
  local i=0
  for t in "${TILES[@]}"; do
    [ -s "$OUT/osm/$1_$i.osm" ] || PYTHONPATH=$V python3 $V/routes2osm.py --kind "$1" --gpkg "$D/$2" --out "$OUT/osm/$1_$i.osm" --bbox $t
    i=$((i+1))
  done
}
conv wanderwege SWISSTLM3D_WANDERWEGE.gpkg
conv wanderland wanderland.gpkg
conv veloland veloland.gpkg
conv mtb mountainbikeland.gpkg
conv ski ski_routes_2056.gpkg
python3 $V/routes/make_typ.py >/dev/null
# name:osm:family-id:beschreibung
for spec in "wanderwege:wanderwege:3911:Wanderwege" "wanderland:wanderland:3912:Wanderland Routen" \
            "veloland:veloland:3913:Veloland Routen" "mountainbike:mtb:3914:Mountainbikeland Routen" \
            "skirouten_blau:ski:3915:Skirouten blau" "skirouten_schwierigkeit:ski:3916:Skirouten nach Schwierigkeit"; do
  IFS=: read name osm fid desc <<<"$spec"
  rm -rf "$OUT/img_$name"; mkdir -p "$OUT/img_$name"
  java -Xmx6g -jar "$JAR" --style-file="$V/routes/style" --output-dir="$OUT/img_$name" \
    --family-id=$fid --product-id=1 --family-name="swisstopo $desc" --series-name="swisstopo $desc" \
    --description="$desc" --mapname=6${fid}001 --code-page=1252 --gmapsupp --keep-going --transparent \
    --draw-priority=30 $(ls "$OUT"/osm/${osm}_*.osm) "$V/routes/typ/$name.txt" | grep -E "Exception|SEVERE" || true
  cp "$OUT/img_$name/gmapsupp.img" "$OUT/swisstopo_$name.img"
done
ls -la "$OUT"/swisstopo_*.img
