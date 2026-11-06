#!/bin/bash
# Baut die Schneeschuhrouten-Karte (eigene .img, Family-ID 3923) aus ch.swisstopo-karto.schneeschuhrouten
# (snowshoe_routes_2056.gpkg, swisstopo/SAC und Winterwanderwege Kt. VS).
#   scripts/build_schneeschuhrouten.sh <snowshoe_routes_2056.gpkg> <mkgmap.jar> <out-ordner> [W S E N]
# Ergebnis: <out>/swisstopo_overlay_schneeschuhrouten.img (Name im Geraetemenue «swisstopo Schneeschuhrouten»)
set -e
G=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
mkdir -p "$OUT"; rm -rf "$OUT/img_schneeschuh"
python3 "$S/make_schneeschuh_typ.py" >/dev/null
if [ $# -eq 4 ]; then BB=(--bbox "$@"); else BB=(); fi
python3 "$S/routes2mkgmap.py" --kind schneeschuh --gpkg "$G" --out "$OUT/schneeschuh.osm" "${BB[@]}"
java -Xmx4g -jar "$JAR" --style-file="$R/mkgmap/schneeschuh/style" --output-dir="$OUT/img_schneeschuh" \
  --family-id=3923 --product-id=1 --family-name="swisstopo Schneeschuhrouten" --series-name="swisstopo Schneeschuhrouten" \
  --description="Schneeschuhrouten" --mapname=63923001 --code-page=1252 --lower-case --gmapsupp --keep-going --transparent \
  --draw-priority=30 "$OUT/schneeschuh.osm" "$R/mkgmap/schneeschuh/typ/schneeschuhrouten.txt" 2>&1 | tee "$OUT/mkgmap_schneeschuh.log" | grep -E "Exception|SEVERE" || true
cp "$OUT/img_schneeschuh/gmapsupp.img" "$OUT/swisstopo_overlay_schneeschuhrouten.img"
ls -la "$OUT/swisstopo_overlay_schneeschuhrouten.img"
