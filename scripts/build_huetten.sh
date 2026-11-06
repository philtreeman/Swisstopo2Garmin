#!/bin/bash
# Baut die Huetten-Karte (eigene .img, Family-ID 3922): Unterkuenfte Winter (SAC/swisstopo) und Huetten aus swissNAMES3D,
# Punkte mit Haussymbol und Name samt Hoehe.
#   scripts/build_huetten.sh <unterkuenfte-winter_2056.gpkg> <swissnames3d_2026_2056.gpkg> <mkgmap.jar> <out-ordner> [W S E N]
# Ergebnis: <out>/swisstopo_overlay_huetten.img (Name im Geraetemenue «swisstopo Huetten»)
set -e
U=$(realpath "$1"); N=$(realpath "$2"); JAR=$(realpath "$3"); OUT=$(realpath -m "$4"); shift 4
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
mkdir -p "$OUT"; rm -rf "$OUT/img_huetten"
python3 "$S/make_huetten_typ.py" >/dev/null
python3 "$S/huetten2mkgmap.py" "$U" "$N" "$OUT/huetten.osm" "$@"
java -Xmx4g -jar "$JAR" --style-file="$R/mkgmap/huetten/style" --output-dir="$OUT/img_huetten" \
  --family-id=3922 --product-id=1 --family-name="swisstopo Huetten" --series-name="swisstopo Huetten" \
  --description="Huetten" --mapname=63922001 --code-page=1252 --lower-case --gmapsupp --keep-going --transparent \
  --draw-priority=31 "$OUT/huetten.osm" "$R/mkgmap/huetten/typ/huetten.txt" 2>&1 | tee "$OUT/mkgmap_huetten.log" | grep -E "Exception|SEVERE" || true
cp "$OUT/img_huetten/gmapsupp.img" "$OUT/swisstopo_overlay_huetten.img"
ls -la "$OUT/swisstopo_overlay_huetten.img"
