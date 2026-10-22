#!/bin/bash
# Baut SwissTOPO Vector, die Vektor-Karte aus swissTLM3D: Strassen, Wege, Siedlungen, Gebaeude, Wald, Fels,
# Geroell, Gewaesser, Bahn, Namen. Darstellung nach der Garmin-Vektorkarte auf dem Edge 1040.
#   [VARIANT=edge|fenix] [GRENZEN=<swissBOUNDARIES3D.gpkg>] scripts/build_vector.sh <shp-ordner> <mkgmap.jar> <out-ordner> [W S E N]
#   VARIANT edge (Standard): Fels mit Textur, Bergnamen mit Hoehe, Gewaesser-, Flur- und Gelaendenamen, Grenzen (braucht GRENZEN)
#   VARIANT fenix: Fels einfach grau, keine Namen ausser der Hoehe an Gipfeln und Paessen, keine Grenzen
#   <shp-ordner>   entpackte swissTLM3D-Shapefiles (swissTLM3D_TLM_*.shp, siehe README)
#   [W S E N]      optionale Bounding Box (WGS84); ohne Angabe: ganze Schweiz
# Umgebungsvariablen: KACHEL_KM (Standard 20), JOBS (parallele Kacheln, Standard 3), SPLIT_MB (Standard 90)
#
# Ablauf:
#   1. vector2mkgmap.py --print-grid     Kachelliste im LV95-Raster (Standard 20 x 20 km)
#   2. je Kachel (parallel, fortsetzbar): swissTLM3D -> OSM-XML -> mkgmap -> <out>/tiles/<Praefix>NNNN.img;
#      das OSM wird danach geloescht (die ganze Schweiz waeren ca. 14 GB)
#   3. mkgmap fuegt alle Kachel-Karten und die TYP-Datei zu <out>/swisstopo_vector_<variante>_schweiz.img (Family-ID 3900/3901, Name im
#      Geraetemenue «SwissTOPO Vector»; mit Bounding Box: swisstopo_vector_region.img) zusammen
#   4. Ist die Datei groesser als SPLIT_MB, entstehen zusaetzlich Teile <name>.img.part_aa, _ab, ...
#      (wiederherstellen mit: cat swisstopo_vector_schweiz.img.part_* > swisstopo_vector_schweiz.img)
# Dauer fuer die ganze Schweiz: ca. 20 Minuten mit 3 Prozessen (4 Kerne, 15 GB RAM). Hoehenlinien fehlen noch.
set -e
SHP=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
KM=${KACHEL_KM:-20}; JOBS=${JOBS:-3}; SPLIT_MB=${SPLIT_MB:-90}
TREES=${TREES:-1}; TREES_FLAG=""; [ "$TREES" = "1" ] && TREES_FLAG="--trees"   # Einzelbaeume (ca. +70 MB)
VARIANT=${VARIANT:-edge}
case "$VARIANT" in
  edge)  FID=3900; PFX=6390; LABEL="SwissTOPO Vector Edge"; GR_FLAG=""
         if [ -n "$GRENZEN" ]; then GR_FLAG="--grenzen $(realpath "$GRENZEN")"; fi
         if [ -n "$ACHSEN" ]; then GR_FLAG="$GR_FLAG --achsen $(realpath "$ACHSEN")"; fi
         if [ -n "$HAUPT" ]; then GR_FLAG="$GR_FLAG --haupt $(realpath "$HAUPT")"; fi ;;
  fenix) FID=3901; PFX=6391; LABEL="SwissTOPO Vector Fenix"; GR_FLAG="" ;;
  *) echo "VARIANT muss edge oder fenix sein"; exit 1 ;;
esac
export VARIANT PFX
STYLE="$R/mkgmap/vector/style"; TYP="$R/mkgmap/vector/typ/swisstopo_vector_$VARIANT.txt"
python3 "$S/make_vector_typ.py" "$VARIANT" >/dev/null
mkdir -p "$OUT/osm" "$OUT/tiles"

BB=(); NAME=swisstopo_vector_${VARIANT}_schweiz
[ $# -eq 4 ] && { BB=(--bbox "$@"); NAME=swisstopo_vector_${VARIANT}_region; }
python3 "$S/vector2mkgmap.py" --print-grid "$KM" "${BB[@]}" > "$OUT/kacheln.txt"
echo "$(wc -l < "$OUT/kacheln.txt") Kacheln a $KM km"

work() {  # work i j x0 y0 x1 y1
  local i=$1 j=$2 name osm
  name=$(printf "%s%04d" "$PFX" $((i*100+j)))              # eindeutiger 8-stelliger Mapname
  [ -e "$OUT/tiles/$name.done" ] && return 0           # fortsetzen: fertige Kacheln ueberspringen
  osm="$OUT/osm/$name.osm"
  python3 "$S/vector2mkgmap.py" --shp "$SHP" --lv95-tile "$3" "$4" "$5" "$6" --out-file "$osm" --variant "$VARIANT" $TREES_FLAG $GR_FLAG >/dev/null 2>&1
  if grep -q "<way" "$osm"; then
    mkdir -p "$OUT/tiles/$name"
    java -Xmx3g -jar "$JAR" --style-file="$STYLE" --output-dir="$OUT/tiles/$name" \
      --family-id=$FID --product-id=1 --mapname="$name" --description="$LABEL" --code-page=1252 --lower-case \
      --draw-priority=20 --remove-short-arcs --reduce-point-density=3 --reduce-point-density-polygon=4 \
      --min-size-polygon=8 --keep-going "$osm" 2>&1 | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
    cp "$OUT/tiles/$name/$name.img" "$OUT/tiles/$name.img"
    rm -rf "$OUT/tiles/$name"
  fi
  rm -f "$osm"; touch "$OUT/tiles/$name.done"
  echo "fertig $name"
}
export -f work; export SHP JAR OUT S STYLE TREES_FLAG FID LABEL GR_FLAG
xargs -P "$JOBS" -L1 bash -c 'work "$@"' _ < "$OUT/kacheln.txt"

mkdir -p "$OUT/final"
java -Xmx6g -jar "$JAR" --output-dir="$OUT/final" --family-id=$FID --product-id=1 \
  --family-name="$LABEL" --series-name="$LABEL" --description="$LABEL" \
  --code-page=1252 --lower-case --gmapsupp "$OUT"/tiles/${PFX}*.img "$TYP" 2>&1 | grep -E "Exception|SEVERE" | grep -v "Exceptions: 0" || true
cp "$OUT/final/gmapsupp.img" "$OUT/$NAME.img"
ls -la "$OUT/$NAME.img"
if [ "$(stat -c%s "$OUT/$NAME.img")" -gt $((SPLIT_MB*1024*1024)) ]; then
  split -b ${SPLIT_MB}m "$OUT/$NAME.img" "$OUT/$NAME.img.part_"
  ls -la "$OUT"/$NAME.img.part_*
fi
