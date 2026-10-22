#!/bin/bash
# Baut das Hoehenlinien-Overlay (Aequidistanz 10 m) aus swissALTI3D als swisstopo_overlay_hoehenlinien.img.
#   scripts/build_hoehenlinien.sh <kachelliste.json> <mkgmap.jar> <out-ordner> [W S E N]
#   <kachelliste.json>  Ergebnis von scripts/swissalti3d_kachelliste.py
#   [W S E N]           optionale Bounding Box (WGS84); ohne Angabe: ganze Schweiz
# Umgebungsvariablen: JOBS (parallele Bloecke, Standard 3), SPLIT_MB (Standard 90), INTERVAL (Standard 10)
#
# Ablauf:
#   1. hoehenlinien2mkgmap.py --print-blocks   Liste der 20-km-Bloecke (LV95-Raster) mit vorhandenen 1-km-Kacheln
#   2. je Block (parallel, fortsetzbar): swissALTI3D-Kacheln laden (je ca. 1 MB), Hoehenlinien rechnen -> OSM -> mkgmap
#      -> <out>/tiles/6391NNNN.img; OSM und Rohdaten werden nicht aufbewahrt
#   3. mkgmap fuegt alle Block-Karten und die TYP-Datei (Family-ID 3917) zu <out>/swisstopo_overlay_hoehenlinien.img zusammen
#   4. Ist die Datei groesser als SPLIT_MB, entstehen Teile <name>.img.part_aa, _ab, ...
set -e
LIST=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
JOBS=${JOBS:-3}; SPLIT_MB=${SPLIT_MB:-90}; INTERVAL=${INTERVAL:-10}
STYLE="$R/mkgmap/overlays/style"; TYP="$R/mkgmap/overlays/typ/hoehenlinien.txt"
python3 "$S/make_overlay_typ.py" >/dev/null
mkdir -p "$OUT/osm" "$OUT/tiles"
BB=(); [ $# -eq 4 ] && BB=(--bbox "$@")
python3 "$S/hoehenlinien2mkgmap.py" --tiles "$LIST" --print-blocks "${BB[@]}" > "$OUT/bloecke.txt"
echo "$(wc -l < "$OUT/bloecke.txt") Bloecke a 20 km"

work() {  # work i j anzahl
  local i=$1 j=$2 name osm
  name=$(printf "6391%04d" $((i*100+j)))
  [ -e "$OUT/tiles/$name.done" ] && return 0
  osm="$OUT/osm/$name.osm"
  python3 "$S/hoehenlinien2mkgmap.py" --tiles "$LIST" --block "$i" "$j" --out "$osm" --interval "$INTERVAL" "${BB[@]}" >/dev/null
  if grep -q "<way" "$osm"; then
    mkdir -p "$OUT/tiles/$name"
    java -Xmx3g -jar "$JAR" --style-file="$STYLE" --output-dir="$OUT/tiles/$name" \
      --family-id=3917 --product-id=1 --mapname="$name" --description="Hoehenlinien 10 m" --code-page=1252 \
      --transparent --draw-priority=30 --remove-short-arcs --keep-going "$osm" 2>&1 \
      | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
    cp "$OUT/tiles/$name/$name.img" "$OUT/tiles/$name.img"
    rm -rf "$OUT/tiles/$name"
  fi
  rm -f "$osm"; touch "$OUT/tiles/$name.done"
  echo "fertig $name"
}
export -f work; export LIST JAR OUT S STYLE INTERVAL; export BB_STR="${BB[*]}"
xargs -P "$JOBS" -L1 bash -c 'BB=($BB_STR); work "$@"' _ < "$OUT/bloecke.txt"

mkdir -p "$OUT/final"
java -Xmx6g -jar "$JAR" --output-dir="$OUT/final" --family-id=3917 --product-id=1 \
  --family-name="swisstopo Hoehenlinien" --series-name="swisstopo Hoehenlinien" --description="Hoehenlinien 10 m" \
  --code-page=1252 --gmapsupp "$OUT"/tiles/6391*.img "$TYP" 2>&1 | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
NAME=swisstopo_overlay_hoehenlinien
cp "$OUT/final/gmapsupp.img" "$OUT/$NAME.img"
ls -la "$OUT/$NAME.img"
if [ "$(stat -c%s "$OUT/$NAME.img")" -gt $((SPLIT_MB*1024*1024)) ]; then
  split -b ${SPLIT_MB}m "$OUT/$NAME.img" "$OUT/$NAME.img.part_"
  ls -la "$OUT"/$NAME.img.part_*
fi
