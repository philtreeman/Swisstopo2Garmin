#!/bin/bash
# Baut die Karte «Unterkuenfte Winter» (eigene .img, Family-ID 3922): alle Unterkuenfte aus ch.swisstopo.unterkuenfte-winter
# als roter Ring wie im swisstopo-Viewer, ergaenzt um SAC- und uebrige Huetten aus swissNAMES3D (kleine Haeuser, nur fein);
# Name samt Hoehe.
#   scripts/build_unterkuenfte_winter.sh <unterkuenfte-winter_2056.gpkg> <swissnames3d_2026_2056.gpkg> <mkgmap.jar> <out-ordner> [W S E N]
# Ergebnis: <out>/swisstopo_overlay_unterkuenfte_winter.img (Name im Geraetemenue «swisstopo Unterkuenfte Winter»)
set -e
U=$(realpath "$1"); N=$(realpath "$2"); JAR=$(realpath "$3"); OUT=$(realpath -m "$4"); shift 4
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
mkdir -p "$OUT"; rm -rf "$OUT/img_unterkuenfte"
python3 "$S/make_unterkuenfte_typ.py" >/dev/null
python3 "$S/unterkuenfte2mkgmap.py" "$U" "$N" "$OUT/unterkuenfte.osm" "$@"
java -Xmx4g -jar "$JAR" --style-file="$R/mkgmap/unterkuenfte/style" --output-dir="$OUT/img_unterkuenfte" \
  --family-id=3922 --product-id=1 --family-name="swisstopo Unterkuenfte Winter" --series-name="swisstopo Unterkuenfte Winter" \
  --description="Unterkuenfte Winter" --mapname=64392201 --code-page=1252 --lower-case --gmapsupp --keep-going --transparent \
  --draw-priority=31 "$OUT/unterkuenfte.osm" "$R/mkgmap/unterkuenfte/typ/unterkuenfte_winter.txt" 2>&1 | tee "$OUT/mkgmap_unterkuenfte.log" | grep -E "Exception|SEVERE" || true
cp "$OUT/img_unterkuenfte/gmapsupp.img" "$OUT/swisstopo_overlay_unterkuenfte_winter.img"
ls -la "$OUT/swisstopo_overlay_unterkuenfte_winter.img"
