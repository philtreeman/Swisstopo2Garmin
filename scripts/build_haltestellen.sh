#!/bin/bash
# Baut die Haltestellen-Karte (eigene .img, Family-ID 3918) aus swissTLM3D: Bus, Bahn, Schiff, uebrige Bahnen mit Namen.
#   scripts/build_haltestellen.sh <shp-ordner> <mkgmap.jar> <out-ordner>
# Ergebnis: <out>/swisstopo_overlay_haltestellen.img (Name im Geraetemenue «swisstopo Haltestellen»)
set -e
SHP=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3")
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
mkdir -p "$OUT"
python3 "$S/make_haltestellen_typ.py" >/dev/null
python3 "$S/haltestellen2mkgmap.py" "$SHP" "$OUT/haltestellen.osm"
java -Xmx4g -jar "$JAR" --style-file="$R/mkgmap/haltestellen/style" --output-dir="$OUT/img" \
  --family-id=3918 --product-id=1 --family-name="swisstopo Haltestellen" --series-name="swisstopo Haltestellen" \
  --description="Haltestellen" --mapname=63918001 --code-page=1252 --gmapsupp --keep-going --transparent \
  --draw-priority=31 "$OUT/haltestellen.osm" "$R/mkgmap/haltestellen/typ/haltestellen.txt" | grep -E "Exception|SEVERE" || true
cp "$OUT/img/gmapsupp.img" "$OUT/swisstopo_overlay_haltestellen.img"
ls -la "$OUT/swisstopo_overlay_haltestellen.img"
