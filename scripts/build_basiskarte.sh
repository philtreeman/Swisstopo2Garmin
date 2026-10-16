#!/bin/bash
# Baut die Basiskarte (Pilot) aus swissTLM3D: Strassen, Wege, Wald, Fels, Gewaesser, Bahn, Gebaeude, Namen.
#   scripts/build_basiskarte.sh <shp-ordner> <mkgmap.jar> <out-ordner> W S E N
#   <shp-ordner>  entpackte swissTLM3D-Shapefiles (swissTLM3D_TLM_*.shp, siehe scripts/download_daten.sh)
# Ergebnis: <out>/swisstopo_basiskarte.img (Family-ID 3900). Hoehenlinien fehlen noch.
set -e
SHP=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
mkdir -p "$OUT/osm" "$OUT/img"
python3 "$S/basiskarte2osm.py" --shp "$SHP" --bbox "$@" --out "$OUT/osm"
java -Xmx6g -jar "$JAR" --style-file="$R/mkgmap/basiskarte/style" --output-dir="$OUT/img" \
  --family-id=3900 --product-id=1 --family-name="swisstopo Basiskarte" --series-name="swisstopo Basiskarte" \
  --description="swisstopo Basiskarte" --mapname=63900001 --code-page=1252 --gmapsupp \
  --draw-priority=20 --remove-short-arcs --reduce-point-density=3 --reduce-point-density-polygon=4 \
  --min-size-polygon=8 --keep-going "$OUT"/osm/*.osm "$R/mkgmap/basiskarte/typ/swisstopo.txt" | grep -E "Exception|SEVERE" || true
cp "$OUT/img/gmapsupp.img" "$OUT/swisstopo_basiskarte.img"
ls -la "$OUT/swisstopo_basiskarte.img"
