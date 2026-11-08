#!/bin/bash
# Baut die Skilifte-Karte (eigene .img, Family-ID 3921) aus ch.swisstopo.bahnen-winter (Landeskarte Winter):
# Skilifte, Sessel-, Gondel-, Luftseil- und Standseilbahnen als Linien mit Namen.
#   scripts/build_skilifte.sh <bahnen-winter_2056.gpkg> <mkgmap.jar> <out-ordner> [W S E N]
# Ergebnis: <out>/swisstopo_overlay_skilifte.img (Name im Geraetemenue «swisstopo Skilifte»)
set -e
G=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
mkdir -p "$OUT"; rm -rf "$OUT/img_skilifte"
python3 "$S/make_skilifte_typ.py" >/dev/null
python3 "$S/skilifte2mkgmap.py" "$G" "$OUT/skilifte.osm" "$@"
java -Xmx4g -jar "$JAR" --style-file="$R/mkgmap/skilifte/style" --output-dir="$OUT/img_skilifte" \
  --family-id=3921 --product-id=1 --family-name="swisstopo Skilifte" --series-name="swisstopo Skilifte" \
  --description="Skilifte" --mapname=64392101 --code-page=1252 --lower-case --gmapsupp --keep-going --transparent \
  --draw-priority=30 "$OUT/skilifte.osm" "$R/mkgmap/skilifte/typ/skilifte.txt" 2>&1 | tee "$OUT/mkgmap_skilifte.log" | grep -E "Exception|SEVERE" || true
cp "$OUT/img_skilifte/gmapsupp.img" "$OUT/swisstopo_overlay_skilifte.img"
ls -la "$OUT/swisstopo_overlay_skilifte.img"
