#!/bin/bash
# Baut die Skipisten-Karte (eigene .img, Family-ID 3926, Menue «OSM Skipisten») aus OpenStreetMap (Auszug OpenStreetMap France,
# switzerland-latest.osm.pbf; Daten © OpenStreetMap-Mitwirkende, ODbL). Einzige OSM-Quelle im Repo.
#   scripts/build_skipisten.sh <switzerland-latest.osm.pbf> <mkgmap.jar> <out-ordner> [W S E N]
# Ergebnis: <out>/swisstopo_overlay_skipisten.img (Kartennummer 64392601)
# Braucht Python mit osmium (pyosmium), shapely; Dauer ca. 3 Minuten, einige hundert MB RAM.
set -e
P=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
mkdir -p "$OUT"; rm -rf "$OUT/img_skipisten"
python3 "$S/make_skipisten_typ.py" >/dev/null
if [ $# -eq 4 ]; then BB=(--bbox "$@"); else BB=(); fi
python3 "$S/skipisten2mkgmap.py" --pbf "$P" --out "$OUT/skipisten.osm" "${BB[@]}" | tee "$OUT/skipisten_zaehlung.txt"
java -Xmx4g -jar "$JAR" --style-file="$R/mkgmap/skipisten/style" --output-dir="$OUT/img_skipisten" \
  --family-id=3926 --product-id=1 --family-name="OSM Skipisten" --series-name="OSM Skipisten" \
  --description="OSM Skipisten" --mapname=64392601 --code-page=1252 --lower-case --gmapsupp --keep-going --transparent \
  --draw-priority=30 --copyright-message="(c) OpenStreetMap-Mitwirkende (ODbL)" \
  "$OUT/skipisten.osm" "$R/mkgmap/skipisten/typ/skipisten.txt" 2>&1 | tee "$OUT/mkgmap_skipisten.log" | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
cp "$OUT/img_skipisten/gmapsupp.img" "$OUT/swisstopo_overlay_skipisten.img"
ls -la "$OUT/swisstopo_overlay_skipisten.img"
