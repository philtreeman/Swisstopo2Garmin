#!/bin/bash
# Baut SwissTOPO Vector, die Vektor-Karte aus swissTLM3D: Strassen, Wege, Siedlungen, Gebaeude, Wald, Fels,
# Geroell, Gewaesser, Bahn, Namen. Darstellung nach der Garmin-Vektorkarte auf dem Edge 1040.
#   scripts/build_vector.sh <shp-ordner> <mkgmap.jar> <out-ordner> [W S E N]
#   <shp-ordner>   entpackte swissTLM3D-Shapefiles (swissTLM3D_TLM_*.shp, siehe README)
#   [W S E N]      optionale Bounding Box (WGS84); ohne Angabe: ganze Schweiz
# Umgebungsvariablen: KACHEL_KM (Standard 20), JOBS (parallele Kacheln, Standard 3), SPLIT_MB (Standard 90)
#
# Ablauf:
#   1. vector2osm.py --print-grid     Kachelliste im LV95-Raster (Standard 20 x 20 km)
#   2. je Kachel (parallel, fortsetzbar): swissTLM3D -> OSM-XML -> mkgmap -> <out>/tiles/6390NNNN.img;
#      das OSM wird danach geloescht (die ganze Schweiz waeren ca. 14 GB)
#   3. mkgmap fuegt alle Kachel-Karten und die TYP-Datei zu <out>/swisstopo_vector_schweiz.img (Family-ID 3900, Name im
#      Geraetemenue «SwissTOPO Vector»; mit Bounding Box: swisstopo_vector_region.img) zusammen
#   4. Ist die Datei groesser als SPLIT_MB, entstehen zusaetzlich Teile <name>.img.part_aa, _ab, ...
#      (wiederherstellen mit: cat swisstopo_vector_schweiz.img.part_* > swisstopo_vector_schweiz.img)
# Dauer fuer die ganze Schweiz: ca. 20 Minuten mit 3 Prozessen (4 Kerne, 15 GB RAM). Hoehenlinien fehlen noch.
set -e
SHP=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
KM=${KACHEL_KM:-20}; JOBS=${JOBS:-3}; SPLIT_MB=${SPLIT_MB:-90}
STYLE="$R/mkgmap/vector/style"; TYP="$R/mkgmap/vector/typ/swisstopo_vector.txt"
python3 "$S/make_vector_typ.py" >/dev/null
mkdir -p "$OUT/osm" "$OUT/tiles"

BB=(); NAME=swisstopo_vector_schweiz
[ $# -eq 4 ] && { BB=(--bbox "$@"); NAME=swisstopo_vector_region; }
python3 "$S/vector2osm.py" --print-grid "$KM" "${BB[@]}" > "$OUT/kacheln.txt"
echo "$(wc -l < "$OUT/kacheln.txt") Kacheln a $KM km"

work() {  # work i j x0 y0 x1 y1
  local i=$1 j=$2 name osm
  name=$(printf "6390%04d" $((i*100+j)))              # eindeutiger 8-stelliger Mapname
  [ -e "$OUT/tiles/$name.done" ] && return 0           # fortsetzen: fertige Kacheln ueberspringen
  osm="$OUT/osm/$name.osm"
  python3 "$S/vector2osm.py" --shp "$SHP" --lv95-tile "$3" "$4" "$5" "$6" --out-file "$osm" >/dev/null 2>&1
  if grep -q "<way" "$osm"; then
    mkdir -p "$OUT/tiles/$name"
    java -Xmx3g -jar "$JAR" --style-file="$STYLE" --output-dir="$OUT/tiles/$name" \
      --family-id=3900 --product-id=1 --mapname="$name" --description="SwissTOPO Vector" --code-page=1252 \
      --draw-priority=20 --remove-short-arcs --reduce-point-density=3 --reduce-point-density-polygon=4 \
      --min-size-polygon=8 --keep-going "$osm" 2>&1 | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
    cp "$OUT/tiles/$name/$name.img" "$OUT/tiles/$name.img"
    rm -rf "$OUT/tiles/$name"
  fi
  rm -f "$osm"; touch "$OUT/tiles/$name.done"
  echo "fertig $name"
}
export -f work; export SHP JAR OUT S STYLE
xargs -P "$JOBS" -L1 bash -c 'work "$@"' _ < "$OUT/kacheln.txt"

mkdir -p "$OUT/final"
java -Xmx6g -jar "$JAR" --output-dir="$OUT/final" --family-id=3900 --product-id=1 \
  --family-name="SwissTOPO Vector" --series-name="SwissTOPO Vector" --description="SwissTOPO Vector" \
  --code-page=1252 --gmapsupp "$OUT"/tiles/6390*.img "$TYP" 2>&1 | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
cp "$OUT/final/gmapsupp.img" "$OUT/$NAME.img"
ls -la "$OUT/$NAME.img"
if [ "$(stat -c%s "$OUT/$NAME.img")" -gt $((SPLIT_MB*1024*1024)) ]; then
  split -b ${SPLIT_MB}m "$OUT/$NAME.img" "$OUT/$NAME.img.part_"
  ls -la "$OUT"/$NAME.img.part_*
fi
