#!/bin/bash
# Baut zwei Hangneigungs-Overlays aus swissALTIRegio (10 m), je eine eigene .img mit eigener Family-ID:
#   swisstopo_overlay_hangneigung.img          Hangneigung 10-20, 20-25, 25-30, 30-35, 35-40, 40-45, 45-50, >50 Grad, 20-m-Raster
#                                              (Family-ID 3924, Kartennummern 643924NN, Menue «swisstopo Hangneigung»)
#   swisstopo_overlay_hangneigungsklassen.img  Lawinen-Hangneigungsklassen ab 30 Grad wie ch.swisstopo.hangneigung-ueber_30, 10-m-Raster
#                                              (Family-ID 3925, Kartennummern 643925NN, Menue «swisstopo Hangneigungsklassen»)
#   scripts/build_hangneigung.sh <swissBOUNDARIES3D.gpkg> <mkgmap.jar> <out-ordner> [W S E N]
#   <swissBOUNDARIES3D.gpkg>  Landesgrenze (Layer tlm_landesgebiet; STAC ch.swisstopo.swissboundaries3d), begrenzt auf CH + FL + 1 km
#   [W S E N]                 optionale Bounding Box (WGS84); ohne Angabe: ganze Schweiz
# Umgebungsvariablen: JOBS (parallele Bloecke, Standard 3; je Block bis ca. 3 GB RAM), SPLIT_MB (Standard 90), DEM (Datei statt URL)
#
# Ablauf:
#   1. hangneigung2mkgmap.py --print-blocks   40-km-Bloecke (LV95-Raster, Ursprung 2480000/1070000) mit laufender Nummer NN
#   2. je Block (parallel, fortsetzbar): Hoehenmodell-Ausschnitt aus dem Cloud-Optimized-GeoTIFF lesen (nichts gespeichert),
#      Neigung einmal rechnen, beide Klassierungen -> zwei OSM-XML (Zwischenformat fuer mkgmap) -> mkgmap -> tiles_*/6439xxNN.img
#   3. mkgmap fuegt je Karte alle Block-Karten und die TYP-Datei zusammen
#   4. Ist eine Datei groesser als SPLIT_MB, entstehen Teile <name>.img.part_aa, _ab, ...
set -e
G=$(realpath "$1"); JAR=$(realpath "$2"); OUT=$(realpath -m "$3"); shift 3
S=$(cd "$(dirname "$0")" && pwd); R=$(dirname "$S")
JOBS=${JOBS:-3}; SPLIT_MB=${SPLIT_MB:-90}
STYLE="$R/mkgmap/hangneigung/style"; TYPDIR="$R/mkgmap/hangneigung/typ"
export CURL_CA_BUNDLE=${CURL_CA_BUNDLE:-/etc/ssl/certs/ca-certificates.crt} GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR GDAL_HTTP_MAX_RETRY=5 GDAL_HTTP_RETRY_DELAY=2
[ -f /root/.ccr/ca-bundle.crt ] && export CURL_CA_BUNDLE=/root/.ccr/ca-bundle.crt
python3 "$S/make_hangneigung_typ.py" >/dev/null
mkdir -p "$OUT/osm" "$OUT/tiles_hangneigung" "$OUT/tiles_klassen"
BB=(); [ $# -eq 4 ] && BB=(--bbox "$@")
DEMARG=(); [ -n "$DEM" ] && DEMARG=(--dem "$DEM")
python3 "$S/hangneigung2mkgmap.py" --grenze "$G" --print-blocks "${BB[@]}" > "$OUT/bloecke.txt"
echo "$(wc -l < "$OUT/bloecke.txt") Bloecke a 40 km"

compile() {  # compile <osm> <tiles-ordner> <mapname> <family-id> <beschreibung>
  local d="$2/$3"
  mkdir -p "$d"
  java -Xmx4g -jar "$JAR" --style-file="$STYLE" --output-dir="$d" \
    --family-id="$4" --product-id=1 --mapname="$3" --description="$5" --code-page=1252 --lower-case \
    --transparent --draw-priority=26 --keep-going "$1" > "$d.log" 2>&1 || true
  grep -E "Exception|SEVERE" "$d.log" | grep -v "Exceptions: 0" || true
  cp "$d/$3.img" "$2/$3.img"; rm -rf "$d"
}

work() {  # work i j nn
  local i=$1 j=$2 nn d
  nn=$(printf "%02d" "$3"); d="$OUT/osm/$i-$j"
  [ -e "$OUT/tiles_klassen/643925$nn.done" ] && return 0
  python3 "$S/hangneigung2mkgmap.py" --grenze "$G" --block "$i" "$j" --out-dir "$d" "${BB[@]}" "${DEMARG[@]}"
  if grep -q "<way" "$d/hangneigung.osm"; then compile "$d/hangneigung.osm" "$OUT/tiles_hangneigung" "643924$nn" 3924 "Hangneigung"; fi
  if grep -q "<way" "$d/klassen.osm"; then compile "$d/klassen.osm" "$OUT/tiles_klassen" "643925$nn" 3925 "Hangneigungsklassen"; fi
  rm -f "$d/hangneigung.osm" "$d/klassen.osm"; rmdir "$d"
  touch "$OUT/tiles_klassen/643925$nn.done"
  echo "fertig Block $i $j -> 643924$nn / 643925$nn"
}
export -f work compile; export G JAR OUT S STYLE; export BB_STR="${BB[*]}" DEM_STR="${DEMARG[*]}"
xargs -P "$JOBS" -L1 bash -c 'BB=($BB_STR); DEMARG=($DEM_STR); work "$@"' _ < "$OUT/bloecke.txt"

for spec in "hangneigung:3924:swisstopo Hangneigung:Hangneigung:hangneigung" \
            "klassen:3925:swisstopo Hangneigungsklassen:Hangneigungsklassen:hangneigungsklassen"; do
  IFS=: read k fid label desc name <<<"$spec"
  rm -rf "$OUT/final_$k"; mkdir -p "$OUT/final_$k"
  java -Xmx6g -jar "$JAR" --output-dir="$OUT/final_$k" --family-id=$fid --product-id=1 \
    --family-name="$label" --series-name="$label" --description="$desc" \
    --code-page=1252 --lower-case --gmapsupp "$OUT"/tiles_$k/6439*.img "$TYPDIR/$name.txt" > "$OUT/mkgmap_final_$k.log" 2>&1
  grep -E "Exception|SEVERE" "$OUT/mkgmap_final_$k.log" || true
  NAME=swisstopo_overlay_$name
  cp "$OUT/final_$k/gmapsupp.img" "$OUT/$NAME.img"
  ls -la "$OUT/$NAME.img"
  rm -f "$OUT"/$NAME.img.part_*
  if [ "$(stat -c%s "$OUT/$NAME.img")" -gt $((SPLIT_MB*1024*1024)) ]; then
    split -b ${SPLIT_MB}m "$OUT/$NAME.img" "$OUT/$NAME.img.part_"
    ls -la "$OUT"/$NAME.img.part_*
  fi
done
